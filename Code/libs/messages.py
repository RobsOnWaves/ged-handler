from emoji import emojize


class Messages:
    nok_string = {'response': "   " + emojize(":no_entry:" + ":musical_note:",
                                              language='alias') + "something went wrong for Fay Wray and King Kong"
                              + emojize(":musical_note:" + ":lips:", language='alias')}

    nok_string_raw = emojize(":no_entry:" + ":musical_note:",language="alias") +\
                     "something went wrong for Fay Wray and King Kong" + \
                     emojize(":musical_note:" + ":lips:", language="alias")

    __ok_string_user_left_side__ = emojize(":ok_woman:", language='alias') + emojize(":+1:", language='alias') \
                                   + "user '"

    __ok_string_user_right_side__ = "' created" + emojize(":kiss:", language='alias')

    __ok_string_user_modified_right_side__ = "' modified" + emojize(":kiss:", language='alias')

    __ok_string_user_action_ok__ = "' action completed with success" + emojize(":kiss:", language='alias')

    denied_entry = emojize(":no_entry:", language="alias") + "you didn't say the magic word"

    def build_ok_user_string(self, user_name: str = ""):
        return self.__ok_string_user_left_side__ + user_name + self.__ok_string_user_right_side__

    def build_ok_action_string(self, user_name: str = ""):
        return self.__ok_string_user_left_side__ + user_name + self.__ok_string_user_action_ok__

    def build_ok_user_modified_string(self, user_name: str = ""):
        return self.__ok_string_user_left_side__ + user_name + self.__ok_string_user_modified_right_side__
