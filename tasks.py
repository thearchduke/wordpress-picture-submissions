import logging

from celery import Celery
import jinja2

from app import app, db
from models import Submission
from wordpress import WordpressAPI


def make_celery(application):
    celery = Celery(
            application.import_name, 
            backend=application.config['CELERY_RESULT_BACKEND'],
            broker=application.config['CELERY_BROKER_URL']
    )
    celery.conf.update(application.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with application.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)


@celery.task()
def make_draft_post(submission_id):
    submission = Submission.query.get(submission_id)
    writer = BJPostWriter(submission)
    return writer.make_draft_post()


class BJPostWriter(object):
    def __init__(self, submission):
        self.wp = WordpressAPI()
        self.submission = submission

    def upload_pictures(self):
        self.upload_results = []
        for picture in self.submission.pictures:
            logging.info("uploading picture %s to wordpress" % picture.id)
            r = self.wp.upload_file(picture.file_location)
            if r.status_code != 201:
                err = "Upload failed for Picture %s, reason: %s" % (
                        picture.id, r.reason
                )
                logging.error(err)
                raise IOError(err)
                break
            self.upload_results.append((picture, r.json()))

    def write_post(self):
        self.post_text = jinja2.Environment(
                loader=jinja2.FileSystemLoader('./templates/')
        ).get_template('draft_post.html').render(
                submission=self.submission,
                upload_results=self.upload_results
        )

    def submit_post(self):
        r = self.wp.post('/wp/v2/posts', params={
                'title': 'On the Road', 
                'status': 'draft',
                'content': self.post_text,
                #'categories': ['On The Road']
                #TODO FIXME wordpress categories are listed by ID here
        })
        if r.status_code != 201:
            err = "Failed to write post for Submission %s, reason: %s" % (
                    self.submission.id, r.text
            )
            logging.error(err)
            raise IOError(err)
        return r.json()

    def make_draft_post(self):
        try:
            self.upload_pictures()
            self.write_post()
        except:
            return False
        self.submission.status = 'submitted'
        db.session.add(self.submission)
        db.session.commit()
        return self.submit_post()
