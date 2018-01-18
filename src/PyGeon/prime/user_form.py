import github
import sender
import requests
import views
import firebasic
reload(views)
from views import post_facebook_message
from sentry.data import PAGE_ACCESS_TOKEN

strings = {
    "GitHub Prompt": "How about showing off your skills ? Can I have your GitHub username ?",
    "Phone Prompt": "Hey I just met you. \nThis is crazy. \nCan I have your number ? \nI'll call you maybe.",
    "Email Prompt": "Can I have your email address too ?",
}

finlist = pd.DataFrame()

temp_dict = {}


def prompt(fbid, prefix, strname):
    #message = sender.opt_select(text=strings["GitHub Prompt"],opts=["Don't have a GitHub"])
    optlist = ['Skip']
    payloads = ['FORM::' + prefix + '::Skip']
    message = sender.gen_button_card(
        strings[strname], optlist, payloads)
    views.post_facebook_message(fbid, message)


class User(object):
    form_queue = [
        ("GH", "GitHub Prompt", store_github_details),
        ("PH", "Phone Prompt", store_phone),
        ("EM", "Email Prompt", store_email)
    ]

    def __init__(self, fbid):
        self.id = fbid
        self.get_profile()
        self.queue_counter = 0

    def get_profile(self):
        params = {"access_token": PAGE_ACCESS_TOKEN}
        r = requests.get(
            'https://graph.facebook.com/v2.11/' + str(self.id), params=params)
        prof = r.json()
        self.img = prof['profile_pic']
        self.name = prof['first_name'] + " " + prof['last_name']
        self.gender = prof['gender']
        self.tz = prof['timezone']

    def store_github_details(self, github_id):
        if github_id is None:
            return False
        self.github_id = github_id
        resp = github.get_user_details(github_id)
        if resp:
            details, self.lseries, self.lang_dict = resp
        else:
            return False
        self.github_url = details['html_url']
        self.loc = details['location']
        self.repo_count = details['public_repos']

    def store_phone(self, num):
        if num is None:
            return False
        self.phone = num

    def store_email(self, eid):
        if eid is None:
            return False
        self.email = eid

    def proc_form(self, mtype, content):
        prev_prompt_opt = form_queue[self.queue_counter]
        if mtype == 'payload':
            pass
        else:
            value = content
            proc_func = prev_prompt_opt[2]
            proc_func(value)
        self.queue_counter += 1
        if self.queue_counter == len(form_queue):
            self.form_flag = False
            self.terminado()
            return False
        prompt_opt = form_queue[self.queue_counter]
        prompt(self.id, prompt_opt[0], prompt_opt[1])

    def start_form(self):
        self.form_flag = True
        self.counter = 0
        prompt_opt = form_queue[self.queue_counter]
        prompt(self.id, prompt_opt[0], prompt_opt[1])

    def to_dict(self):
        return {
            'messenger_id': self.id,
            'name': self.name,
            'sex': self.gender,
            'email': self.email,
            'github_url': self.github_url,
            'fb_image': self.img,
            'loc': self.loc,
            'repo_count': self.repo_count,
            'phone': self.phone,
            'timezone': self.tz,
            'langs': self.lseries.to_dict()
        }

    def terminado(self):
        col = firebasic.get_col('Users')
        firebasic.add_record(col, self.id, self.to_dict())
        del temp_dict[self.id]


x = User(1645332865512512)
