      


from pyd2bot.dofus.datacenter.monsters.MonsterBonusCharacteristics import MonsterBonusCharacteristics
from pyd2bot.dofus.datacenter.monsters.monster import Monster


class MonsterGrade:
      
   
   grade:int
   
   monsterId:int
   
   level:int
   
   vitality:int
   
   paDodge:int
   
   pmDodge:int
   
   wisdom:int
   
   earthResistance:int
   
   airResistance:int
   
   fireResistance:int
   
   waterResistance:int
   
   neutralResistance:int
   
   gradeXp:int
   
   lifePoints:int
   
   actionPoints:int
   
   movementPoints:int
   
   damageReflect:int
   
   hiddenLevel:int
   
   strength:int
   
   intelligence:int
   
   chance:int
   
   agility:int
   
   bonusRange:int
   
   startingSpellId:int
   
   bonusCharacteristics:MonsterBonusCharacteristics = None
   
   _monster:Monster
   
   def __init__(self):
      super().__init__()
   
   @property
   def monster(self) -> Monster:
      if not self._monster:
         self._monster = Monster.getMonsterById(self.monsterId)
      return self._monster
   
   @property
   def static(self) -> bool:
      return self.movementPoints == -1