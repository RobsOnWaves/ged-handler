
db = new Mongo().getDB("GED");

db = new Mongo().getDB("USERS");

db.users.createIndex({ "user_name": 1 }, { unique: true })

db.users.insert({
    "user_name": "admin",

    "admin": {
        "username": "admin",
        "full_name": "first_name last_name",
        "email": "dummy@test.com",
        "hashed_password": "$2y$10$yaTEx9h67DhcpNIXiyKm6.0aer4b5TwdGRgTgF1yFCZQtrTl2GZ7u",
        "disabled": false,
        "created_at": ISODate("1986-06-16T17:00:00.000+02:00"),
        "created_by": "init_script",
        "role": "admin"
    }

}
)


db.users.insert({
    "user_name": "user",

    "user": {
        "username": "user",
        "full_name": "user",
        "email": "dummy@test.com",
        "hashed_password": "$2y$10$ZDzTTO0vC7KYHvS9AvN8DOP40FNn3DG1ujwV5PmawK0.GJz9pSMHC",
        "disabled": false,
        "created_at": ISODate("1986-06-16T17:00:00.000+02:00"),
        "created_by": "init_script",
        "role": "user"
    }

}
)

