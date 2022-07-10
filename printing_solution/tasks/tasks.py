import time
import typing
import datetime as dt

import flask

import printing_solution.extensions as extensions

DEFAULT_RESULT_TTL = 0
MAX_TIME_BEFORE_RESUBMIT = 20  # minutes

MAX_TIME_BEFORE_RETRY = 30  # seconds
MAX_ITERATION = 32


# 10 minutes time out 60*10
@extensions.rq.job(result_ttl=DEFAULT_RESULT_TTL, ttl=20 * 60, timeout=60 * 10)
def async_send_printing_request(ticket_number: str,
                                qr: str,
                                min_start_time: typing.Optional[str] = None,
                                iteration: int = 1):
    """
    Send printing request to cloud asynchronously.
    """
    def reschedule():
        if iteration <= MAX_ITERATION:
            async_send_printing_request.queue(
                queue=extensions.DEFAULT_QUEUE,
                iteration=iteration + 1,
                # In the event of failure we set min_start_time to be 30 seconds in the future
                min_start_time=(dt.datetime.utcnow() + dt.timedelta(seconds=MAX_TIME_BEFORE_RETRY)).isoformat(),
                ticket_number=ticket_number,
                qr=qr
            )
        else:
            flask.current_app.logger.info(f"Tried maximum number of times to reschedule job")

    try:
        flask.current_app.logger.info(f"Sending request for ticket:{ticket_number} with qr: {qr}")

        if min_start_time:
            # If min_start_time exists that means the last attempt was a failure
            # we wait 30 seconds before sending another request to cloud printer
            wait_period = (dt.datetime.fromisoformat(min_start_time) - dt.datetime.utcnow()).seconds
            if wait_period > 0:
                flask.current_app.logger.info(f"Waiting {wait_period} seconds to be processed again")
                time.sleep(wait_period)

        # We can use printing service to send payload
        order_id: typing.Optional[str] = extensions.print_service.send_printing_request(ticket_number=ticket_number,
                                                                                        qr=qr)

        if not order_id:
            flask.current_app.logger.info(f"No order id found calling rq job again. "
                                          f"Total number of iteration: {iteration}")
            reschedule()

    except Exception as e:
        flask.current_app.logger.warning(
            f"Job Failure - {e}")
        reschedule()


def queue_async_send_printing_request(job_id: str, **args):
    return __queuer(
        fn=async_send_printing_request.queue,
        job_id=job_id,
        **args
    )


def __queuer(fn: typing.Callable, job_id: str, **args) -> bool:
    # This is not atomic, but a double run is not a terrible thing
    job = extensions.rq.get_queue(name=extensions.DEFAULT_QUEUE).fetch_job(job_id)
    # Because flask_rq2 is rather old, we cannot add a failure_ttl to jobs. This means we may have failed jobs
    # waiting to be processed. In effect, all the conditions below are trying to detect such a scenario.
    if not job or job.created_at < dt.datetime.utcnow() - dt.timedelta(minutes=MAX_TIME_BEFORE_RESUBMIT) or \
            job.is_failed or job.is_canceled or job.is_stopped or job.is_deferred:
        # Call async printing task.
        fn(job_id=job_id, queue=extensions.DEFAULT_QUEUE, **args)
        return True
    flask.current_app.logger.warning(f"will not queue job {job_id} - already queued at {job.created_at}")
    return False
