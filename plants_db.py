import sqlite3
from database import init_db

# Функция для добавления растения
def add_plant(name, photo, info, watering_interval, spraying_interval, fertilizing_interval):
    conn = sqlite3.connect('plants.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO plants (name, photo, info, watering_interval, spraying_interval, fertilizing_interval)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, photo, info, watering_interval, spraying_interval, fertilizing_interval))
    conn.commit()
    conn.close()
    print(f"Растение '{name}' успешно добавлено в базу данных!")

# Список растений для добавления
plants_to_add = [
    {
        "name": "монстера ⋆˚࿔",
        "photo": "https://architecturaldigest.pl/i/publications/278/1920_1080/monstera-deliciosa-uprawa-podlewanie-stanowisko-odmiany-wszystko-co-musisz-wiedziec-o-monsterze-dziurawej-1838-278-19114.jpg",
        "info": "для стимуляции роста монстеры, в период с апреля по август проводят специальные подкормки. вносить дополнительные питательные вещества рекомендуем каждые две недели, чередуя минеральные удобрения с органическими. ദ്ദി(˵ •̀ ᴗ - ˵ ) ✧",
        "watering_interval": 7,
        "spraying_interval": 3,
        "fertilizing_interval": 30
    },
    {
        "name": "кактус ⋆˙⟡",
        "photo": "https://plantsforallseasons.com/wp-content/uploads/2020/08/pfas-collect-colorful-cute-cacti-header.jpg",
        "info": "в жару полив производят вечером, а в прохладную и облачную погоду — утром. лесные кактусы удобряют ежемесячно, а пустынные — два раза в месяц. изредка (2–3 раза за сезон) рекомендуется подкислять воду лимонной кислотой. на литр воды кладут лимонную кислоту на кончике ножа. ( ˶ˆᗜˆ˵ )",
        "watering_interval": 14,
        "spraying_interval": 0,  # Не требует опрыскивания
        "fertilizing_interval": 30
    },
    {
        "name": "денежное дерево ✮⋆˙",
        "photo": "https://porady.24tv.ua/resources/photos/news/202408/2627511.jpg?v=1724753682000",
        "info": "с конца весны до середины лета толстянку подкармливают специальным удобрением для кактусов и других суккулентов один раз в месяц. она нуждается в достаточном количестве яркого света. вместо опрыскиваний – протирание влажной тканевой салфеткой. >⩊<",
        "watering_interval": 21,
        "spraying_interval": 0,
        "fertilizing_interval": 30
    },
    {
        "name": "суккулент -`♡´-",
        "photo": "https://home-ideas.ru/wp-content/uploads/2016/07/oblozhka-8-870x400.png",
        "info": "суккуленты любят сухой воздух и перепады температур. достаточно хорошо проветривать помещения, не держать их во влажном месте, стараться обеспечить максимальный перепад дневной-ночной температуры и помнить, что заморозки они уж точно не любят. опрыскивать нельзя. ᓚ₍⑅^..^₎♡",
        "watering_interval": 14,
        "spraying_interval": 0,
        "fertilizing_interval": 30
    },
    {
        "name": "кротон ⋆⭒˚.⋆",
        "photo": "https://s13.stc.all.kpcdn.net/family/wp-content/uploads/2021/12/kroton-2.jpg",
        "info": "лучше поливать небольшим количеством воды несколькими порциями регулярно, чем лить большое количество сразу. для Кротона нужно как минимум 5 часов хорошего света в день. поэтому желательно поместить эти комнатные растения прямо перед окном на востоке, западе или севере. (๑>◡<๑)",
        "watering_interval": 4,
        "spraying_interval": 0,
        "fertilizing_interval": 30
    },
    {
        "name": "юкка ༘⋆",
        "photo": "https://cdn.galleries.smcloud.net/t/galleries/gf-ADyk-Q613-ZUJv_juka-domowa-664x442-nocrop.jpg",
        "info": "любит яркие, но не прямые лучи солнца. очень хорошо подойдут южные и западные подоконники. считается, что цветок драцены юкки приносит в дом уют, мир и благополучие, а в офис – удачу в бизнесе. ฅ^>⩊<^ฅ",
        "watering_interval": 7,
        "spraying_interval": 7,
        "fertilizing_interval": 15
    },
    {
        "name": "лаванда ୭ ˚. ᵎᵎ",
        "photo": "https://www.livemint.com/lm-img/img/2023/08/12/1600x900/pexels-anastasia-shuraeva-5126290_1691826522675_1691826533608.jpg",
        "info": "лаванде требуется в день не менее 6 часов солнечного света. ૮₍´˶• . • ⑅ ₎ა",
        "watering_interval": 7,
        "spraying_interval": 0,
        "fertilizing_interval": 21
    }
]

if __name__ == '__main__':
    init_db()  # Инициализация базы данных
    for plant in plants_to_add:
        add_plant(
            name=plant["name"],
            photo=plant["photo"],
            info=plant["info"],
            watering_interval=plant["watering_interval"],
            spraying_interval=plant["spraying_interval"],
            fertilizing_interval=plant["fertilizing_interval"]
        )