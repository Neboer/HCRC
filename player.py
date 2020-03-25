from datetime import datetime


class Player:
    index = 0
    name = ""
    password = ""
    create_time = None
    invitation = []

    def __init__(self, index, name, password, create_timestamp, invitor, invitation_code_list, invite_player_list):
        self.index = index
        self.name = name
        self.password = password
        self.create_time = datetime.fromtimestamp(create_timestamp)
        self.invitor_name = invitor
        self.invitation = []
        for i in range(len(invitation_code_list)):
            self.invitation.append((invitation_code_list[i], invite_player_list[i]))
