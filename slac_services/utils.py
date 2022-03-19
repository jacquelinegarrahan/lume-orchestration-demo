import datetime
import yaml, re, os

# misc utilities

def flatten_dict(d):
    def expand(key, value):
        if isinstance(value, dict):
            return [(k, v) for k, v in flatten_dict(value).items()]
        else:
            return [(key, value)]

    items = [item for k, v in d.items() for item in expand(k, v)]

    return dict(items)

"""UTC to ISO 8601 with Local TimeZone information without microsecond"""
def isotime():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).astimezone().replace(microsecond=0).isoformat()    



def load_yaml_with_env_vars(filepath):

    #MATCH REGEX AND SUB
    env_pattern = re.compile(r".*?\${(.*?)}.*?")
    def env_constructor(loader, node):
        value = loader.construct_scalar(node)
        for group in env_pattern.findall(value):
            if not os.environ.get(group):
                raise ValueError(f"Environment variable {group} is not defined")
            value = value.replace(f"${{{group}}}", os.environ.get(group))

        return value

    # ADD RESOLVER AND CONSTRUCTOR
    yaml.add_implicit_resolver("!pathex", env_pattern, None, yaml.SafeLoader)
    yaml.add_constructor("!pathex", env_constructor, yaml.SafeLoader)

    with open(filepath, 'r') as file:
        config = yaml.safe_load(file)


    return config
