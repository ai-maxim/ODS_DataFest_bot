import traceback

from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.error import Unauthorized
from telegram.ext import run_async, MessageHandler, Filters
from django.db.models import Count

from backend.google_spreadsheet_client import GoogleSpreadsheet
from backend.models import TGUser, Invite, Prizes
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.texts import *
from backend.tgbot.tghandler import TGHandler
from backend.tgbot.utils import logger, Decorators


class MainMenu(TGHandler):
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def check_registration_status(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_ENTER_EMAIL, reply_markup=ReplyKeyboardRemove())
        return self.CHECK_REGISTRATION_STATUS

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def authorization(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_ENTER_EMAIL, reply_markup=ReplyKeyboardRemove())
        return self.AUTHORIZATION

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def get_news(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        if user.has_news_subscription:
            custom_keyboard = [[BUTTON_NEWS_UNSUBSCRIPTION,
                                BUTTON_FULL_BACK
                                # BUTTON_GET_LAST_5_NEWS
                                ]]
        else:
            custom_keyboard = [[BUTTON_NEWS_SUBSCRIPTION,
                                BUTTON_FULL_BACK
                                # BUTTON_GET_LAST_5_NEWS
                                ]]
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_NEWS, reply_markup=ReplyKeyboardMarkup(custom_keyboard
                                                                              , one_time_keyboard=True
                                                                              , resize_keyboard=True))
        return self.GET_NEWS

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def participate_random_prize(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        if user.merch_size is None:
            update.message.reply_text(TEXT_CHOOSE_YOUR_SIZE, reply_markup=ReplyKeyboardMarkup(self.SIZE_KEYBOARD,
                                                                                              one_time_keyboard=True,
                                                                                              resize_keyboard=True))
            return self.CHOOSEN_SIZE
        else:
            custom_keyboard = [[BUTTON_CHANGE_SIZE, BUTTON_FULL_BACK]]
            update.message.reply_text(TEXT_KNOW_SIZE.format(user.merch_size)
                                      , reply_markup=ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True,
                                                                         resize_keyboard=True))
            return self.CHANGE_SIZE

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def not_ready_yet(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_NOT_READY_YET, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def get_schedule(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_NOT_READY_YET, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def show_path(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_NOT_READY_YET, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    # ADMIN
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def create_broadcast(self, api: TelegramBotApi, user: TGUser, update):
        logger.info("User %s initiated broadcast.", user)
        if not user.is_admin:
            update.message.reply_text(TEXT_NOT_ADMIN, reply_markup=self.define_keyboard(user))
        update.message.reply_text(TEXT_ENTER_BROADCAST)
        return self.BROADCAST

    # REFRESH INVITES
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def refresh_invites_and_notify(self, api: TelegramBotApi, user: TGUser, update):
        gss_client = GoogleSpreadsheet(client_secret_path='./backend/tgbot/client_secret.json')
        logger.info("User %s initiated invites refresh.", user)
        if not user.is_admin:
            update.message.reply_text(TEXT_NOT_ADMIN, reply_markup=self.define_keyboard(user))
            return self.MAIN_MENU
        update.message.reply_text(TEXT_START_INVITE_REFRESH)
        try:
            new_invites_count = gss_client.update_invites()
            update.message.reply_text(TEXT_REPORT_INVITE_COUNT.format(new_invites_count))
            notification_count = send_notifications(api)
            update.message.reply_text(TEXT_REPORT_NOTIFICATION_COUNT.format(notification_count),
                                      reply_markup=self.define_keyboard(user))
        except:
            update.message.reply_text(TEXT_REPORT_INVITE_REFRESH_ERROR + '\n' + traceback.format_exc(),
                                      reply_markup=self.define_keyboard(user))
            logger.exception('error updating invites')
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def draw_prizes(self, api: TelegramBotApi, user: TGUser, update):
        if not user.is_admin:
            update.message.reply_text(TEXT_NOT_ADMIN, reply_markup=self.define_keyboard(user))
            return self.MAIN_MENU
        logger.info("User %s choose draw prizes.", user)
        group_by_merch = TGUser.objects.values('merch_size').annotate(dcount=Count('merch_size'))
        users_merch_table = ''
        for row in group_by_merch:
            users_merch_table += '\n' + str(row.get('merch_size')) + ' : ' + str(row.get('dcount'))

        prizes_info = Prizes.objects.values()
        prizes_table = ''
        for row in prizes_info:
            prizes_table += '\n' + str(row.get('merch_size')) + ' : ' + str(row.get('quantity'))

        update.message.reply_text(TEXT_START_RANDOM_PRIZE.format(users_merch_table, prizes_table)
                                  , reply_markup=ReplyKeyboardMarkup([[BUTTON_START_DRAWING, BUTTON_FULL_BACK]]
                                                                     , one_time_keyboard=True,
                                                                     resize_keyboard=True))
        return self.DRAW_PRIZES

    # @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    # def who_is_your_daddy(self, api: TelegramBotApi, user: TGUser, update):
    #     return self.MAIN_MENU  # Nope
    #     text = update.message.text
    #     logger.info('User {} have chosen {} '.format(user, text))
    #     if user.is_admin:
    #         user.is_admin = False
    #         user.save()
    #         update.message.reply_text('God mode :off', reply_markup=self.define_keyboard(user))
    #     else:
    #         user.is_admin = True
    #         user.save()
    #         update.message.reply_text('God mode :on', reply_markup=self.define_keyboard(user))
    #     return self.MAIN_MENU

    def create_state(self):
        state = {self.MAIN_MENU: [
            self.rhandler(BUTTON_CHECK_REGISTRATION, self.check_registration_status),
            self.rhandler(BUTTON_AUTHORISATION, self.authorization),
            self.rhandler(BUTTON_NEWS, self.get_news),
            self.rhandler(BUTTON_SCHEDULE, self.get_schedule),
            self.rhandler(BUTTON_SHOW_PATH, self.show_path),

            self.rhandler(BUTTON_PARTICIPATE_IN_RANDOM_PRIZE, self.participate_random_prize),
            self.rhandler(BUTTON_RANDOM_BEER, self.not_ready_yet),

            self.rhandler(BUTTON_REFRESH_SCHEDULE, self.not_ready_yet),
            self.rhandler(BUTTON_SEND_INVITES, self.refresh_invites_and_notify),
            #self.rhandler(BUTTON_DRAW_PRIZES, self.draw_prizes),
            self.rhandler(BUTTON_DRAW_PRIZES, self.not_ready_yet),
            self.rhandler(BUTTON_POST_NEWS, self.create_broadcast),

            # self.rhandler('88224646BA', self.who_is_your_daddy),

            # self.rhandler(BUTTON_CREATE_BROADCAST, self.create_broadcast)
            MessageHandler(Filters.text, self.unknown_command)
        ]}
        return state


def send_notifications(api: TelegramBotApi):
    count = 0

    for user in TGUser.objects.exclude(is_notified=True). \
            exclude(last_checked_email='').exclude(is_authorized=True).all():
        invite = Invite.objects.filter(email=user.last_checked_email).first()
        if invite is not None:
            try:
                api.bot.send_message(user.tg_id, TEXT_INVITE_NOTIFICATION)
                user.is_notified = True
                user.save()
            except Unauthorized:
                logger.info('{} blocked'.format(user))
            count += 1
    return count