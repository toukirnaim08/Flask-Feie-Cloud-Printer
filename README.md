## Ticket printing using Feie Cloud Printer

Cloud printing refers to the technology that printing equipment obtains printing information and executes printing in different places through broadband, WiFi, 4G and other networks. Different from the previous printing methods such as USB and other wired networks or local area wireless networks, there are no restrictions on distance and location. Customers place orders remotely through various methods, and the store prints the order content through cloud printing equipment.

Cloud printing technology helps merchants improve operational efficiency, and integrates Fei'e cloud services to open up more business scenarios.

Feie cloud service api details can be found on http://www.feieyun.com/open/apidoc-en.html.
And all the availble tags for printing tickets are given below, for example ```<BR>``` is used for new line.

```
<BR> : Line break
<CUT> : Cutter command (active cutting, only effective when using cutter printer)
<LOGO> : Print LOGO command (provided that the LOGO picture is built in the machine in advance)
<PLUGIN> : Cash drawer or external audio command
<CB></CB> : Center to zoom in
<B></B> : Double the zoom
<C></C> : Centered
<L></L> : The font is doubled
<W></W> : The font is doubled
<QR></QR> : QR code (single order, only one QR code can be printed at most)
<RIGHT></RIGHT> : Align right
<BOLD></BOLD> : bold font
  Print barcode (one-dimensional barcode) and order layout to align, click to download the following function reference, if you have other technical questions, please join Feiye API open platform 5 group: 146903613.
```

This flask application is desgined to work on some specific feie models such as FP-58W,FP-80WC and FP-58WC.


## Running Application locally

Run the following commands to bootstrap your environment if you are unable to run the application using Docker

```bash
cd printing-solution
pip install -r requirements.txt
flask run
```

## Running the Service via Docker
run "run_docker_build.sh" bash to create docker image and dont forget to change your docker id.

```shell
chmod +x ./run_docker_build.sh
./run_docker_build.sh
```
After creating image successfully you can execute the following command to run the docker image.

```shell
docker run --network=host \
-e LOG_LEVEL='info' \
-e PRINTER_SN='sn' \
-e PRINTER_KEY='key' \
-e RQ_REDIS_URL='redis://localhost:6379/0' \
-- <YOUR_DOCKER_ID>/printing-solution-production:latest
```

## Running Redis Workers

The workers are launched due to the configuration that can be found in supervised_processes/*.conf.

To run them in a dev environment, you need to:
* Set FLASK_APP variable: FLASK_APP=autoapp-worker.py
* Run: python3 -m flask rq worker printing-default
  * the queue will typically be printing-queue

Worker wont work on windwos as The rq library uses os.fork that is not available on Windows.
And dont forget to run redis locally. If you dont have redis installed, you run redis via docker.


```
 docker run -d -p 6379:6379 --name redis redis:latest
```
user RQ_REDIS_URL to connect worker with redis

```
RQ_REDIS_URL=redis://localhost:6379/0
```

A test is implemented with around 80% of coverage.
Finally, open swagger ui on http://127.0.0.1:5000/
