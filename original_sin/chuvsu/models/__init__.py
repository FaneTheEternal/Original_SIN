from django.db import models

from .profile import VkUser, QuestProfile
from .step import ChatStep, ProxyStep


class BotProfile2(models.Model):
    user_guid = models.TextField()

    current = models.TextField(default='')
    back = models.TextField(verbose_name='cls1;cls2', help_text='work as stack', default='')

    def get_step(self, pool):
        for item in pool:
            if item.__name__ == self.current:
                return item
        return None

    def get_back(self, pool):
        back = self.back.split(';')
        if back:
            back = back[-1]
            for name, chat in pool.items():
                if name == back:
                    return chat
        return None

    def set_step(self, new):
        frames = self.back.split(';')
        if new in frames:
            frames = frames[:frames.index(new)]
        else:
            frames.append(self.current)
        self.back = ';'.join(frames)
        self.current = new
        self.save()
