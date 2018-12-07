from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from databaseSetup import Category, Item, User, Base

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

categories = ['Soccer', 'Basketball', 'Baseball', 'Frisbee', 'Snowboarding', 'Rock Climbing', 'Foosball', 'Skating', 'Hockey', 'Table Tennis']
#creates user in order to assign an owner for all the items
newUser = User(name = "Rohan Wadhwa", email = "rohan.avatar@gmail.com")
session.add(newUser)
session.commit()
#adds all necessary categories in the database
for category in categories:
    newCategory = Category(name = category)
    session.add(newCategory)
    session.commit()

user = session.query(User).filter_by(email = "rohan.avatar@gmail.com").one()
#adds category items for Soccer
category = session.query(Category).filter_by(name = "Soccer").one()
session.add(Item(name = "Soccer Ball", category = category, user = user))
session.add(Item(name = "Soccer Cleats", category = category, description = "Shoes created specifically for soccer that allow you to up your game and play safer and better", user = user))
session.add(Item(name = "Shinguards", category = category, description = "Important safety item that allows you to protect damage to your shin", user = user))
session.add(Item(name = "Jersey", category = category, user = user))
session.commit()

#adds category items for Basketball
category = session.query(Category).filter_by(name = "Basketball").one()
session.add(Item(name = "Basketball", category = category, user = user))
session.add(Item(name = "Basketball Shoes", category = category, description = "Shoes created specifically for basketball that allow you to up your game and play safer and better", user = user))
session.add(Item(name = "Jersey", category = category, user = user))
session.commit()

#adds category items for Baseball
category = session.query(Category).filter_by(name = "Baseball").one()
session.add(Item(name = "Bat", category = category, description = "Used to hit the ball", user = user))
session.add(Item(name = "Baseball", category = category, user = user))
session.add(Item(name = "Catcher's mitt", category = category, description = "Used by the catcher to catch the ball", user = user))
session.add(Item(name = "Baseball cleats", category = category, description = "Shoes created specifcially for baseball that allow you to up your game and play safer and better", user = user))
session.add(Item(name = "Jersey", category = category, user= user))
session.commit()

#adds category items for Frisbee
category = session.query(Category).filter_by(name = "Frisbee").one()
session.add(Item(name = "Frisbee", category = category, user = user))
session.commit()

#adss category items for Snowboarding
category = session.query(Category).filter_by(name = "Snowboarding").one()
snowboardDescription = "Best for any terrain and conditions. All-mountain snowboards perform anywhere on a mountain - groomed runs, backcountry, even park and pipe. They may be directional (meaning downhill only) or twin-tip (for riding switch, meaning either direction). Most boarders ride all-mountain boards. Because of their versatility, all-mountain boards are good for beginners who are still learning what terrain they like."
session.add(Item(name = "Snowboard", category = category, description = snowboardDescription, user = user))
session.add(Item(name = "Goggles", category = category, user = user))
session.commit()

#adds category items for Foosball
category = session.query(Category).filter_by(name="Foosball").one()
session.add(Item(name = "Foosball Table", category = category, user = user))
session.commit()

#adds category items for Skating
category = session.query(Category).filter_by(name="Skating").one()
session.add(Item(name = "Ice Skates", category = category, description = "Used for skating on ice", user = user))
session.add(Item(name = "Roller Skates", category = category, description ="Used for skating on the ground", user = user))
session.commit()

#adds category items for Hockey
category = session.query(Category).filter_by(name="Hockey").one()
session.add(Item(name="Stick", category = category, user = user))
session.add(Item(name="Puck", category = category, description = "Used for ice hockey", user = user))
session.add(Item(name= "Ball", category = category, description = "Used for field hockey", user = user))
session.commit()

#adds category items for Table Tennis
category = session.query(Category).filter_by(name = "Table Tennis").one()
session.add(Item(name = "Paddle", category = category, user = user))
session.add(Item(name="Ball", category = category, user = user))
session.commit()

categories = session.query(Category).all()
items = session.query(Item).all()
