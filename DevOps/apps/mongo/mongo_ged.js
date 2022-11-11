use GED

use USERS

db.users.createIndex({ "user_name": 1 }, { unique: true })

db.users.insert({
    "user_name": "robinator",

    "robinator": {
        "username": "robinator",
        "full_name": "Robin Cohen-Selmon",
        "email": "robinator@ged-api.com",
        "hashed_password": "$2b$12$7jcW/wJzwt4yl9naxz8c3ObWqTUMp7kzPxrD2DJC1EmkbzymRsL12",
        "disabled": false,
        "created_at": ISODate("1986-06-16T17:00:00.000+02:00"),
        "created_by": "The One",
        "role": "admin"
    }

}
)


db.users.insert({
    "user_name": "user",

    "user": {
        "username": "user",
        "full_name": "user",
        "email": "user@ged-api.com",
        "hashed_password": "$2y$10$YxdfAHfGJy.yOl.ZUKUDVe3AH3BSwsrpDe/DgkN89HRT5UYsmQGE6",
        "disabled": false,
        "created_at": ISODate("1986-06-16T17:00:00.000+02:00"),
        "created_by": "The other One",
        "role": "user"
    }

}
)

