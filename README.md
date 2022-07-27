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

#### Get a specific message field by message name

```bash
curl http://127.0.0.1:2609/get/message/GLOBAL_POSITION_INT/relative_alt
```

```json
{"relative_alt":-17}
```

#### Get a specific message field by message id

```bash
curl http://127.0.0.1:2609/get/message/33/alt
```

```json
{"alt":584070}
```

#### Get all parameters

```bash
curl http://127.0.0.1:2609/get/parameter/all
```

#### Get a specific parameter by name

```bash
curl http://127.0.0.1:2609/get/parameter/STAT_RUNTIME
```

```json
{"STAT_RUNTIME":{"statistics":{"average_frequency":0.04563327537308594,"counter":3,"duration":43.82766706199618,"first":1659120473.6298168,"first_monotonic":41638.127151403,"instant_frequency":0.03223455110705248,"last":1659120517.4574845,"last_monotonic":41681.954818465,"latency":31.022612868997385},"value":8897.0}}
```

#### Get all plan

```bash
curl http://127.0.0.1:2609/get/plan/all
```

#### Get a specific mission plan item by id

```bash
curl http://127.0.0.1:2609/get/plan/1
```

```json
{"autocontinue":1,"command":22,"current":0,"frame":3,"mission_type":0,"param1":0.0,"param2":0.0,"param3":0.0,"param4":0.0,"seq":1,"statistics":{"average_frequency":0,"counter":1,"duration":0,"first":1659097224.3198915,"first_monotonic":20229.831076511,"instant_frequency":0,"last":1659097224.3198915,"last_monotonic":20229.831076511,"latency":0},"target_component":0,"target_system":255,"x":0,"y":0,"z":50.0}
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
| plan     | bool  | True                    | Fetch plan                                                                                   |