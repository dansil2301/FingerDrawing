from Server.Enums.HandPosition import HandPosition


class Gestures:
    def _hand_position(self, wrist, mid_mcp) -> HandPosition:
        # what can be: ✋, 🫲, 🫱 (this not AI I promise...)
        x_len = mid_mcp.x - wrist.x 
        y_len = wrist.y - mid_mcp.y

        # ✋
        if y_len > 0 and y_len > abs(x_len):
            return HandPosition.UP
        # 🫱
        elif x_len > 0 and x_len > abs(y_len):
            return HandPosition.RIGHT
        # 🫲
        elif x_len < 0 and abs(x_len) > abs(y_len):
            return HandPosition.LEFT
        # ✋ this but upside down
        elif y_len < 0 and abs(y_len) > abs(x_len):
            return HandPosition.DOWN
        else:
            return HandPosition.NULL
        
    def _finger_open(self, tip, dip, pip, wrist, mid_mcp) -> bool:
        position = self._hand_position(wrist, mid_mcp)

        # rar = rearanged
        if position == HandPosition.UP:
            rar_tip, rar_dip, rar_pip = -tip.y, -dip.y, -pip.y
        elif position == HandPosition.RIGHT:
            rar_tip, rar_dip, rar_pip = tip.x, dip.x, pip.x
        elif position == HandPosition.LEFT:
            rar_tip, rar_dip, rar_pip = -tip.x, -dip.x, -pip.x
        elif position == HandPosition.DOWN:
            rar_tip, rar_dip, rar_pip = tip.y, dip.y, pip.y
        else:
            return False

        return rar_tip > rar_dip > rar_pip
        
    def _thumb_open(self, hand: list) -> bool:
        thumb_tip = hand[4]
        thumb_ip = hand[3]
        thumb_mcp = hand[2]

        wrist = hand[0]
        mid_mcp = hand[13]
        pinky_mcp = hand[17]

        position = self._hand_position(wrist, mid_mcp)
        if position == HandPosition.NULL:
            return False

        if position == HandPosition.UP:
            is_right_hand = thumb_mcp.x < pinky_mcp.x
            return thumb_tip.x < thumb_ip.x if is_right_hand else thumb_tip.x > thumb_ip.x

        elif position == HandPosition.DOWN:
            is_right_hand = thumb_mcp.x > pinky_mcp.x
            return thumb_tip.x > thumb_ip.x if is_right_hand else thumb_tip.x < thumb_ip.x

        elif position == HandPosition.RIGHT:
            is_right_hand = thumb_mcp.y > pinky_mcp.y
            return thumb_tip.y > thumb_ip.y if is_right_hand else thumb_tip.y < thumb_ip.y

        elif position == HandPosition.LEFT:
            is_right_hand = thumb_mcp.y < pinky_mcp.y
            return thumb_tip.y < thumb_ip.y if is_right_hand else thumb_tip.y > thumb_ip.y

        return False

    def index(self, hand: list):
        fingers = {
            'thumb': self._thumb_open(hand),
            'index': self._finger_open(hand[8], hand[7], hand[6], hand[0], hand[13]),
            'middle': self._finger_open(hand[12], hand[11], hand[10], hand[0], hand[13]),
            'ring': self._finger_open(hand[16], hand[15], hand[14], hand[0], hand[13]),
            'pinky': self._finger_open(hand[20], hand[19], hand[18], hand[0], hand[13]),
        }

        return fingers