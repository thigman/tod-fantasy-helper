import json, random
from dataclasses import dataclass
from enum import Enum

class RangeBand(Enum):
    MEL='MEL'
    OOM='OOM'
    OOB='OOB'

@dataclass
class Weapon:
    name:str; damage:str; pen:int

@dataclass
class Hero:
    name:str; hp:int; max_hp:int; arm:int
    str_:int; dex:int; ms:int; rs:int; intel:int
    weapon:Weapon; damage_done:int=0

@dataclass
class Enemy:
    name:str; hp:int; max_hp:int; arm:int; spd:int
    str_:int; dex:int; ms:int; morale:int; pack:int
    weapon:Weapon; rng:RangeBand
    focus_target:str|None=None
    focus_rounds:int=0

def roll(expr):
    n,s=map(int,expr.split('d'))
    return sum(random.randint(1,s) for _ in range(n))

def menu(title, items):
    print(f'\n{title}')
    for i,x in enumerate(items,1): print(f'{i}. {x}')
    while True:
        try:
            v=int(input('> '))
            if 1<=v<=len(items): return v-1
        except: pass
        print('Invalid selection')

def save_party(heroes):
    with open('party.json','w') as f:
        json.dump([h.name for h in heroes],f,indent=2)

fightersword=Weapon('LSWD','1d8',2)
axe=Weapon('AXE','1d8',2)
bow=Weapon('BOW','1d6',1)

heroes=[
Hero('Fighter',25,25,4,7,5,7,1,2,fightersword),
Hero('Wizard',12,12,1,2,4,2,2,8,Weapon('MM','1d8',2))]

def hero_state(h,acted):
    if h.hp<=0: return 'DEAD'
    if h.name in acted: return 'ACTED'
    return 'READY'

def show_heroes(acted):
    for i,h in enumerate(heroes,1):
        print(f'{i}. {h.name} HP{max(0,h.hp)}/{h.max_hp} STR{h.str_} DEX{h.dex} MS{h.ms} ARM{h.arm} {h.weapon.name}({h.weapon.damage}) {hero_state(h,acted)}')

def show_enemies(enemies):
    for i,e in enumerate(enemies,1):
        focus=f' -> {e.focus_target}' if e.focus_target else ''
        print(f'{i}. {e.name} HP{max(0,e.hp)}/{e.max_hp} STR{e.str_} DEX{e.dex} MS{e.ms} ARM{e.arm} SPD{e.spd} {e.weapon.name}({e.weapon.damage}) {e.rng.value}{focus}')

def choose_focus(enemy, targets):
    return max(targets,key=lambda x:x.damage_done+5)

def build_encounter():
    enemies=[]; ow=1; oa=1
    while True:
        print('\n=== ENCOUNTER BUILDER ===')
        if enemies:
            show_enemies(enemies); print('TOTAL:',len(enemies))
        else:
            print('No enemies yet.')
        c=menu('Builder',['Add Orc Warrior','Add Orc Archer','Start Encounter'])
        if c==2: return enemies
        if c==0:
            enemies.append(Enemy(f'Orc Warrior #{ow}',16,16,3,2,6,4,6,5,7,axe,RangeBand.OOM)); ow+=1
        if c==1:
            enemies.append(Enemy(f'Orc Archer #{oa}',12,12,1,1,4,5,4,5,5,bow,RangeBand.OOM)); oa+=1

enemies=build_encounter(); acted=set(); log=[]; rnd=1; enemies_defeated=0
while enemies:
    print(f'\n=== ROUND {rnd} ===')
    print('\nHEROES'); show_heroes(acted)
    print('\nENEMIES'); show_enemies(enemies)

    c=menu('Action',['Attack','Set Enemy Range','Status','Enemy Turn','Combat Log','Save Party','Quit'])

    if c==6: break
    if c==5: save_party(heroes); print('Saved'); continue
    if c==4: print(*log[-20:],sep='\n'); continue
    if c==2: continue

    if c==1:
        idx=menu('Choose Enemy',[e.name for e in enemies])
        r=menu('Range',['MEL - In Melee','OOM - Out of Melee','OOB - Out of Battle'])
        enemies[idx].rng=list(RangeBand)[r]
        continue

    if c==0:
        avail=[h for h in heroes if h.hp>0 and h.name not in acted]
        if not avail:
            print('No living heroes available.')
            continue
        hero=avail[0] if len(avail)==1 else avail[menu('Hero',[h.name for h in avail])]
        enemy=enemies[menu('Enemy',[e.name for e in enemies])]

        if hero.name=='Wizard':
            sp=menu('Spell',['Magic Missile','Fireball'])
            dmgexpr='1d8' if sp==0 else '2d8'
            pen=2 if sp==0 else 0
            hit=random.randint(1,20)+hero.intel >= 10+enemy.dex
        else:
            if enemy.rng!=RangeBand.MEL:
                print('Target not in melee')
                continue
            dmgexpr=hero.weapon.damage
            pen=hero.weapon.pen
            hit=random.randint(1,20)+hero.ms >= 10+enemy.ms

        msg=f'{hero.name} misses {enemy.name}'
        if hit:
            dmg=max(1,roll(dmgexpr)-max(enemy.arm-pen,0))
            enemy.hp-=dmg
            hero.damage_done+=dmg
            msg=f'{hero.name} hits {enemy.name} for {dmg}'

        print(msg); log.append(msg); acted.add(hero.name)
        defeated=sum(1 for e in enemies if e.hp<=0)
        enemies_defeated += defeated
        enemies=[e for e in enemies if e.hp>0]
        continue

    if c==3:
        print('\nENEMY TURN')
        group_hp_pct=(sum(max(0,e.hp) for e in enemies)*100)//max(1,sum(e.max_hp for e in enemies))

        for e in enemies:
            hp_pct=(max(0,e.hp)*100)//e.max_hp
            score=e.morale+e.pack+random.randint(1,10)
            threshold=15-(group_hp_pct//10)

            if hp_pct<=25 and score<threshold:
                m=f'{e.name} breaks and attempts to retreat.'
                print(m); log.append(m); continue

            if hp_pct<=50 and score<threshold:
                m=f'{e.name} loses nerve and attempts to withdraw.'
                print(m); log.append(m); continue

            if e.weapon.name=='BOW' and e.rng==RangeBand.MEL:
                m=f'{e.name} attempts to withdraw.'
                print(m); log.append(m); continue

            targets=[h for h in heroes if h.hp>0]
            if not targets:
                break

            current_target=None
            if e.focus_target:
                current_target=next((h for h in targets if h.name==e.focus_target),None)

            if current_target is None or e.focus_rounds<=0:
                current_target=choose_focus(e,targets)
                e.focus_target=current_target.name
                e.focus_rounds=2

            if e.weapon.name=='AXE' and e.rng==RangeBand.OOM:
                m=f'{e.name} attempts to advance toward {current_target.name}.'
                print(m); log.append(m); continue

            tgt=current_target
            hit=random.randint(1,20)+e.ms >= 10+tgt.ms

            if hit:
                dmg=max(1,roll(e.weapon.damage)-max(tgt.arm-e.weapon.pen,0))
                tgt.hp-=dmg
                msg=f'{e.name} hits {tgt.name} for {dmg}'
            else:
                msg=f'{e.name} misses {tgt.name}'

            if e.focus_rounds>0:
                e.focus_rounds-=1

            print(msg); log.append(msg)

        acted.clear(); rnd+=1

print('\n=== BATTLE OVER ===')
print('\n=== BATTLE SUMMARY ===')
print(f'Rounds: {rnd - 1}')
print(f'Enemies Defeated: {enemies_defeated}')
print('\nHeroes:')
for h in heroes:
    print(f'{h.name}: HP {max(0,h.hp)}/{h.max_hp}  Damage Done {h.damage_done}')

while True:
    print('\n=== POST BATTLE ===')
    print('1. View Full Combat Log')
    print('2. Quit')
    try:
        choice=int(input('> '))
    except:
        choice=0
    if choice==1:
        print('\n=== FULL COMBAT LOG ===')
        if not log:
            print('No combat log entries.')
        else:
            for entry in log:
                print(entry)
    elif choice==2:
        break
print('Game Over')
