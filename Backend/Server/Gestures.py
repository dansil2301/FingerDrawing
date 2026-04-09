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
            is_looking_right = thumb_mcp.x < pinky_mcp.x
            return thumb_tip.x < thumb_ip.x if is_looking_right else thumb_tip.x > thumb_ip.x

        elif position == HandPosition.DOWN:
            is_looking_left = thumb_mcp.x > pinky_mcp.x
            return thumb_tip.x > thumb_ip.x if is_looking_left else thumb_tip.x < thumb_ip.x

        elif position == HandPosition.RIGHT:
            is_looking_down = thumb_mcp.y > pinky_mcp.y
            return thumb_tip.y > thumb_ip.y if is_looking_down else thumb_tip.y < thumb_ip.y

        elif position == HandPosition.LEFT:
            is_looking_up = thumb_mcp.y < pinky_mcp.y
            return thumb_tip.y < thumb_ip.y if is_looking_up else thumb_tip.y > thumb_ip.y

        return False
    
    def _fingers(self, hand: list):
         return {
            'thumb': self._thumb_open(hand),
            'index': self._finger_open(hand[8], hand[7], hand[6], hand[0], hand[9]),
            'middle': self._finger_open(hand[12], hand[11], hand[10], hand[0], hand[9]),
            'ring': self._finger_open(hand[16], hand[15], hand[14], hand[0], hand[9]),
            'pinky': self._finger_open(hand[20], hand[19], hand[18], hand[0], hand[9]),
        }

    def index(self, hand: list):
        fingers = self._fingers(hand)
        # had to disable thumb to its highly movable nature, so basically if 
        # middle, ring, pinky are down then index can be detected
        return fingers['index'] and all([not fingers[f] for f in fingers if f != 'index' and f != 'thumb'])
    
    def fully_open(self, hand: list):
        fingers = self._fingers(hand)
        return all([fingers[f] for f in fingers])
