# Pymavrest

## Installation
```bash
cd $HOME
git clone https://github.com/mustafa-gokce/pymavrest.git
cd pymavrest/
/usr/bin/python3 -m pip install -r requirements.txt
```

## Usage

### Run

```bash
/usr/bin/python3 pymavrest.py
 ```

### Endpoints

#### Get all messages

```bash
curl http://127.0.0.1:2609/get/message/all
```

Sample data can be found in the [sample.json](sample.json) file.

```bash
curl https://raw.githubusercontent.com/mustafa-gokce/pymavrest/main/sample.json
```

#### Get a specific message by name

```bash
curl http://127.0.0.1:2609/get/message/GLOBAL_POSITION_INT
```

```json
{"alt":584070,"hdg":35196,"lat":-353632620,"lon":1491652373,"relative_alt":-17,"statistics":{"average_frequency":3.992716958686398,"counter":938,"duration":234.92774712200026,"first":1658392158.7851973,"first_monotonic":6634.220171939,"instant_frequency":3.978920063475837,"last":1658392393.7129443,"last_monotonic":6869.147919061,"latency":0.25132447600026353},"time_boot_ms":2327066,"vx":1,"vy":-1,"vz":0}
```

#### Get a specific message by message id

```bash
curl http://127.0.0.1:2609/get/message/33
```

#### Get all parameters

```bash
curl http://127.0.0.1:2609/get/parameter/all
```

#### Get a specific parameter by name

```bash
curl http://127.0.0.1:2609/get/parameter/STAT_RUNTIME
```

### Advanced run and query

```bash
/usr/bin/python3 pymavrest.py --host="127.0.0.1" --port=2609 --master="udpin:127.0.0.1:14550" --timeout=5.0 --drop=5.0 --white="GLOBAL_POSITION_INT,ATTITUDE,VFR_HUD" --black="VFR_HUD" --param=True
```

```bash
curl http://127.0.0.1:2609/get/message/all
```

```json
{"ATTITUDE":{"pitch":-0.0012523328186944127,"pitchspeed":-0.0002957125543616712,"roll":-0.001061532530002296,"rollspeed":-0.00020833441521972418,"statistics":{"average_frequency":4.453590722351151,"counter":10,"duration":2.2453792059995976,"first":1658392455.4101565,"first_monotonic":6930.84513167,"instant_frequency":3.9732811780329746,"last":1658392457.6555388,"last_monotonic":6933.090510876,"latency":0.25168115599990415},"time_boot_ms":2390818,"yaw":-0.13986118137836456,"yawspeed":-0.0007141817477531731},"GLOBAL_POSITION_INT":{"alt":584070,"hdg":35199,"lat":-353632620,"lon":1491652373,"relative_alt":-17,"statistics":{"average_frequency":4.453193604230211,"counter":10,"duration":2.245579440000256,"first":1658392455.410245,"first_monotonic":6930.845220089,"instant_frequency":3.9706995252477864,"last":1658392457.6558244,"last_monotonic":6933.090799529,"latency":0.251844792999691},"time_boot_ms":2390818,"vx":1,"vy":-1,"vz":0}}
```

## Arguments

| Argument | Type  | Default                 | Help                                                                                         |
|----------|-------|-------------------------|----------------------------------------------------------------------------------------------|
| host     | str   | "127.0.0.1"             | Pymavrest server IP address                                                                  |
| port     | int   | 2609                    | Pymavrest server port number                                                                 |
| master   | str   | "udpin:127.0.0.1:14550" | Standard MAVLink connection string                                                           |
| timeout  | float | 5.0                     | Try to reconnect after this seconds when no message is received, zero means do not reconnect |
| drop     | float | 5.0                     | Drop non-periodic messages after this seconds, zero means do not drop                        |
| white    | str   | ""                      | Comma separated white list to filter messages, empty means all messages are in white list    |
| black    | str   | ""                      | Comma separated black list to filter messages                                                |
| param    | bool  | True                    | Fetch parameters                                                                             |
