import json
import os


def load_keys_from_json(file_path="token_key.json"):
    """从 JSON 文件加载密钥。"""
    with open(file_path, "r") as file:
        return json.load(file)


def set_environment_variables(keys):
    """设置环境变量。"""
    for key, value in keys.items():
        os.environ[key] = value
        # 直接修改系统的环境变量
        os.system(f'echo "export {key}={value}" >> /etc/environment')


def get_environment_variables(json_keys=None):
    """获取环境变量。"""
    if json_keys is not None:
        return {key: os.environ.get(key) for key in json_keys}
    else:
        return dict(os.environ)


def check_env(json_file_path="token_key.json"):
    """检查环境变量并打印每个变量与 JSON 文件的比较结果。"""
    json_keys = load_keys_from_json(json_file_path)
    env_vars = get_environment_variables(json_keys.keys())
    all_passed = True

    print("Checking environment variables:")
    for key, json_value in json_keys.items():
        env_value = env_vars.get(key)
        if env_value is None:
            print(f"{key} missing !")
        elif env_value == json_value:
            print(f"{key} pass")
        else:
            print(f"{key} different ! (JSON: {json_value}, Env: {env_value})")
            all_passed = False
            print(
                "Different environment variables detected. Please check the JSON file and environment variables.\nProcess terminated."
            )
            return all_passed

    return all_passed


def write_and_check_env(json_file_path="token_key.json"):
    """从 JSON 文件加载密钥，设置环境变量，然后检查。"""
    json_keys = load_keys_from_json(json_file_path)
    set_environment_variables(json_keys)
    print("Environment variables set from JSON file and written to /etc/environment.")
    return check_env(json_file_path)


def export_example_json():
    """创建一个示例 JSON 文件, 通过已有的token_key.json的key, value则简单的都是example好了。"""
    example_json = {key: "example" for key in load_keys_from_json().keys()}
    with open("example_token_key.json", "w") as file:
        json.dump(example_json, file, indent=4)


def init_json():
    """读取example_token_key.json文件, 将不存在的key添加到token_key.json文件中。"""
    example_keys = load_keys_from_json("example_token_key.json")
    token_keys = load_keys_from_json("token_key.json")
    for key, value in example_keys.items():
        if key not in token_keys:
            token_keys[key] = value
    with open("token_key.json", "w") as file:
        json.dump(token_keys, file, indent=4)


def try_env():
    print("Initial environment check:")
    initial_check = check_env()
    if not initial_check:
        return
    print(f"\nInitial check result: {initial_check}")

    print("\nSetting and checking environment variables:")
    final_check = write_and_check_env()
    print(f"\nFinal check result: {final_check}")


if __name__ == "__main__":
    try_env()
    export_example_json()
    init_json()
