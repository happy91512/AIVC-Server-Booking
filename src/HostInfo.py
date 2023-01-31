from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List
import yaml

# https://github.com/yaml/pyyaml/issues/127#issuecomment-525800484
class CustomDumper(yaml.SafeDumper):
    def write_line_break(self, data=None):
        super().write_line_break(data)

        if len(self.indents) == 1:
            super().write_line_break()


def load_yaml(filename: str) -> dict:
    with open(filename, 'r') as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


def dump_yaml(info_dict: dict, filename: str):
    with open(filename, 'w') as f:
        yaml.dump(info_dict, f, Dumper=CustomDumper, sort_keys=False)
    return True


@dataclass
class UserConfig:
    password: str = None
    forward_port: int = None  # which forward port you want to connect to port: 22(SSH).
    image: Path = None  # which image you want to use, default is use "rober5566a/aivc-server:latest"
    extra_command: str = None  # the extra command you want to execute when the docker runs.
    volume_work_dir: Path = None
    volume_dataset_dir: Path = None
    volume_backup_dir: Path = None

    def to_dict(self):
        self.dict = asdict(self)
        return self.dict


class UsersConfig:
    ids: Dict[str, UserConfig]

    def __init__(self, yaml_file='users_config.yaml') -> None:
        self.ids = self.get_users_config(yaml_file)

    @staticmethod
    def get_users_config(yaml_file='users_config.yaml') -> Dict[str, UserConfig]:
        users_dict = load_yaml(yaml_file)
        users_config = {}
        for k, v in users_dict.items():
            users_config[k] = UserConfig(**v)

        return users_config

    def to_dict(self):
        self.dict = {}
        for k in self.ids.keys():
            self.dict[k] = self.ids[k].to_dict()
        return self.dict


class MaxCapability:
    cpus: int
    ram: int
    swap_size: int
    gpus: int

    shm_rate: int
    memory: int

    def __init__(self, full_dict: dict) -> None:
        for k, v in full_dict.items():
            if k == 'shm_rate' or k == 'memory':
                setattr(self, k, eval(v, {'ram': self.ram, 'swap_size': self.swap_size}))
            else:
                setattr(self, k, v)


class BasicCapability:
    cpus: int
    memory: int
    gpus: int

    def __init__(
        self,
        cpus: int or str = None,
        memory: int or str = None,
        gpus: int or str = None,
        defaultCap: object = None,
        maxCap: MaxCapability = None,
    ) -> None:
        cap_str_ls = ['cpus', 'memory', 'gpus']
        for cap_str in cap_str_ls:
            cap_value = locals()[cap_str]
            if type(cap_value) is int:
                setattr(self, cap_str, cap_value)
            elif type(cap_value) is str:
                setattr(self, cap_str, getattr(maxCap, cap_str))
            else:
                setattr(self, cap_str, getattr(defaultCap, cap_str))


class CapabilityConfig:
    max: MaxCapability
    allow_stdID: List[str]
    max_default_capability: BasicCapability
    max_custom_capability: Dict[str, BasicCapability]

    def __init__(self, yaml='capability_config.yaml') -> None:
        for k, v in load_yaml(yaml).items():
            if k == 'max':
                setattr(self, k, MaxCapability(v))
            elif k == 'max_default_capability':
                setattr(self, k, BasicCapability(**v))
            elif k == 'max_custom_capability':
                custom_dict = {}
                for k_sub, v_sub in v.items():
                    custom_dict[k_sub] = BasicCapability(**v_sub, defaultCap=self.max_default_capability, maxCap=self.max)
                setattr(self, k, custom_dict)
            else:
                setattr(self, k, v)


class HostDeployInfo:
    capability_config_yaml: str
    users_config_yaml: str

    volume_work_dir: str
    volume_dataset_dir: str
    volume_backup_dir: str

    def __init__(self, yaml_file='host_deploy.yaml') -> None:
        for k, v in load_yaml(yaml_file).items():
            setattr(self, k, v)


if __name__ == '__main__':
    # host_info = HostDeployInfo('./cfg/test_host_deploy.yaml')

    # CapCfg = CapabilityConfig(
    #     host_info.capability_config_yaml,
    # )

    # print(dir(host_info))
    # print(host_info)

    # userCig = UserConfig()
    # print(userCig.to_dict())
    # print(userCig.dict)

    import copy

    users_config = UsersConfig('./cfg/test_users_config.yaml')
    user_config = copy.deepcopy(users_config.ids['m11007s05'])
    print(id(user_config), id(users_config))
    print(users_config.ids['m11007s05'] == user_config)
