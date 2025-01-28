class Stats():
    stats = {
        "health": 0,
        "attack": 1,
        "defense": 2
    }

    @staticmethod
    def get_index(key):
        return Stats.stats[key]

class DamageCalculator:
    def __init__(self):
        #healt, atk, def
        stats_P1 = [100, 12, 10]
        stats_P2 = [100, 12, 10]
        self.players = [stats_P1, stats_P2]

    def Add_To_Stat(self, player, type_str, value):
        type_index = Stats.get_index(type_str)
        print(f"player {player} new {type_str}: {value}")
        self.players[player][type_index] += value

    def Attack(self, attacker_index, defender_index, attacker_posture, defender_posture, bonus_atk = 0, bonus_def = 0):
        if attacker_posture != "Attack":
            return 0, self.is_alive(defender_index)

        attacker_atk = self.players[attacker_index][1] + bonus_atk
        defender_def = self.players[defender_index][2] + bonus_def

        damage = self.calculate_damage(defender_posture, attacker_atk, defender_def)
        self.players[defender_index][0] -= damage
        return damage, self.is_alive(defender_index)

    def calculate_damage(self, defender_posture, attacker_atk, defender_def):
        raw_damage = attacker_atk - defender_def

        print(raw_damage, self.players)

        if defender_posture == "Def":
            damage = int(raw_damage / 2)
        else:
            damage = raw_damage
        return damage

    def is_alive(self, player):
        return self.players[player][0] > 0
