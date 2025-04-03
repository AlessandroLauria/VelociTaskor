from .TelegramNotifier import TelegramNotifier


class Notifier():

    def __init__(self):
        self.config = {
            "telegram": {
                "active": True,
                "token": "",
                "chat_id": ""
            }
        }

        self.sys_instances = self.get_systems()

    def get_systems(self):
        sys_instances = []
        for system in self.config.keys():
            if self.config[system]["active"]:
                if system == "telegram":
                    sys_instances.append(TelegramNotifier(self.config[system]["token"], self.config[system]["chat_id"]))

        return sys_instances

    def send_task_notification(self, task_data):
        for system in self.sys_instances:
            system.send_task_notification(task_data)

