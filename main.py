import os
import random
import requests
import logging
import twitter
from apscheduler.schedulers.blocking import BlockingScheduler
import config


def send_telegram_bot_message(msg: str, to_admin: bool = False):
    url = f'https://api.telegram.org/bot{config.CONFIG["telegram_token"]}/sendMessage'
    response = requests.post(url, {
        "chat_id": config.CONFIG["user_chat_id"],
        "text": msg
    }).json()
    logging.info(response)

    if to_admin:
        response = requests.post(url, {
            "chat_id": config.CONFIG["admin_chat_id"],
            "text": msg
        }).json()
        logging.info(response)


def swap_image_folders():
    logging.info("Ran out of images, switching folders.")
    os.rename(config.CONFIG['images_backlog_folder'], f"{config.CONFIG['images_backlog_folder']}bkp")
    os.rename(config.CONFIG['images_base_folder'], config.CONFIG['images_backlog_folder'])
    os.rename(f"{config.CONFIG['images_backlog_folder']}bkp", config.CONFIG['images_base_folder'])


def get_random_image_from_folder():
    images = os.listdir(config.CONFIG["images_base_folder"])
    if len(images) == 0:
        swap_image_folders()
        images = os.listdir(config.CONFIG['images_base_folder'])

    image_path = images[random.randint(0, len(images) - 1)]
    full_image_path = f"{config.CONFIG['images_backlog_folder']}/{image_path}"
    os.rename(f"{config.CONFIG['images_base_folder']}/{image_path}", full_image_path)
    return open(full_image_path, "rb")


def post_random_image():
    api = twitter.Api(consumer_key=config.CONFIG['api_key'],
                      consumer_secret=config.CONFIG['api_key_secret'],
                      access_token_key=config.CONFIG['access_token'],
                      access_token_secret=config.CONFIG['access_token_secret'])
    # Try 128 times
    for i in range(128):
        try:
            with get_random_image_from_folder() as image:
                logging.info(f"Trying to post image: {image.name}")
                status = api.PostUpdate(status="", media=image)
                logging.info(f"Posted image: {image.name}\n\t\t{status}")
                send_telegram_bot_message("New post was published.")
                return
        except Exception as e:
            logging.error(f"An error has occurred {e} with image {image.name}")
            send_telegram_bot_message(f"An error has occurred {e} with image {image.name}", True)
        finally:
            image.close()


def main():
    logging.basicConfig(filename="twitterBot.log", filemode='w', level=logging.DEBUG,
                        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
    logging.info("Twitter Bot is starting...")
    send_telegram_bot_message("Twitter Bot is starting...", True)

    scheduler = BlockingScheduler()
    scheduler.add_job(post_random_image, 'cron', hour='*')
    scheduler.start()


if __name__ == '__main__':
    if not os.path.isdir(config.CONFIG['images_base_folder']):
        os.mkdir(config.CONFIG['images_base_folder'])
    if not os.path.isdir(config.CONFIG['images_backlog_folder']):
        os.mkdir(config.CONFIG['images_backlog_folder'])

    main()
