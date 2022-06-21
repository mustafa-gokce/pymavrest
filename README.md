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

#### Get a specific message by name

```bash
curl http://127.0.0.1:2609/get/message/GLOBAL_POSITION_INT
```

```json
{"alt":584070,"hdg":35197,"lat":-353632620,"lon":1491652373,"relative_alt":-17,"time_boot_ms":1148808,"vx":1,"vy":-1,"vz":0}
```

#### Get a specific message by message id

```bash
curl http://127.0.0.1:2609/get/message/33
```

#### Get all message statuses

```bash
curl http://127.0.0.1:2609/get/status/all
```

#### Get a specific status by message name

```bash
curl http://127.0.0.1:2609/get/status/GLOBAL_POSITION_INT
```

```json
{"clock":1658320471.5939665,"frequency":3.974224057142368,"latency":0.25162144499699934,"monotonic":18751.838395392}
```

#### Get a specific status by message id

```bash
curl http://127.0.0.1:2609/get/status/33
```

### Advanced run and query

```bash
/usr/bin/python3 pymavrest.py --host="127.0.0.1" --port=2609 --master="udpin:127.0.0.1:14550" --timeout=5.0 --drop=5.0 --white="GLOBAL_POSITION_INT,ATTITUDE,VFR_HUD" --black="VFR_HUD"
```

```bash
curl http://127.0.0.1:2609/get/message/all
```

```json
{"ATTITUDE":{"pitch":0.0008510049665346742,"pitchspeed":0.00023347508977167308,"roll":0.0010392718249931931,"rollspeed":0.00027910646167583764,"time_boot_ms":1837558,"yaw":-0.1311929076910019,"yawspeed":0.00020906582358293235},"GLOBAL_POSITION_INT":{"alt":584070,"hdg":35249,"lat":-353632621,"lon":1491652375,"relative_alt":-17,"time_boot_ms":1837558,"vx":-1,"vy":1,"vz":0}}
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
