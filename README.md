# hetzner-dyndns
A small python script that accesses the Hetzner API to update DNS records that sends out a warning email if some tasks failed.

## General
I know that this script is kind of overkill for this simple task. Also by all this functionality it could offer a way more flexible configuration for example.
But since this was just a fun experience for me messing around with Python functions and stuff I didn't bother putting too much effort into creating a "professional script". 

## Usage
### Configuration
Clone the repository into your desired location then create a customized configuration file in your desired location. It doesn't have to be named `conf.json`, that's just my preference. You can specify a config file name when executing the script.

The configuration names are pretty self-explanatory; Get your API key from Hetzner as well as all your desired Zone ID with the reffering Record IDs. Then add all records that you want to be updated to the configuration file (two examples are already there).

### Run it
Running the script is straightforward. By default the log level is set to `INFO` and logs will be stored in the script location. The default configuration file name is `/script-execution-path/conf.json`.

For more details make use of the *help* parameter as seen below;
```
./hetzner-dyndns.py --help
```

### Crontab
In most cases you want the script to be run on a scheduled basis. For this I am using the following crontab configuration;
```
*/5 * * * * ~/git/hetzner-dyndns/hetzner-dyndns.py
```


