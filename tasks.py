import logging

from wordpress import WordpressAPI


wp = WordpressAPI()

def li_from_picture(picture):
    result = wp.upload_file(picture.file_location)
    if result.status_code != 201:
        err = "Upload failed for Picture %s" % picture.id
        logging.error(err)
        raise IOError(err)
    result_json = result.json()
    paragraph = result_json['description']['rendered']
    return "<li>%s</li>" % paragraph
