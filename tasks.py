import logging

import jinja2

from wordpress import WordpressAPI


class BJPostWriter(object):
    def __init__(self, submission):
        self.wp = WordpressAPI()
        self.submission = submission

    def upload_pictures(self):
        self.upload_results = []
        for picture in self.submission.pictures:
            r = self.wp.upload_file(picture.file_location)
            if r.status_code != 201:
                err = "Upload failed for Picture %s, reason: %s" % (
                        picture.id, r.reason
                )
                logging.error(err)
                raise IOError(err)
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
                'title': 'On The Road', 
                'status': 'draft',
                'content': self.post_text
        })
        if r.status_code != 201:
            err = "Failed to write post for Submission %s, reason: %s" % (
                    self.submission.id, r.reason
            )
            logging.error(err)
            raise IOError(err)
        return r

    def make_draft_post(self):
        self.upload_pictures()
        self.write_post()
        return self.submit_post()
