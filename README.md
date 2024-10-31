#Overview

Note: Pyprizm could use console.out function and indent flag for console.log

Note: Need console.out and console.full

Example Script
```
{
	"user": {
		"*id:int": {},
		"fname:str": {"regex": "", "limit": 32},
		"lname:str": {"regex": "", "limit": 32},
		"email:str!": {"regex": "email", "limit": 100},
		"gender:bool": {},
		"bio:str": {"limit": 300}
	},
	"follower": {
		"*id:int": {},
		"@user->id=follower_id:int!": {},
		"@user->id=followee_id:int!": {}
	},
	"post": {
		"*id:int": {},
		"content:str": {"limit": 300},
		"@user->id:int!": {}
	},
	"comment": {
		"*id:int": {},
		"content:str": {"limit": 300},
		"@user->id:int!": {},
		"@post->id:int!": {}
	},
	"like": {
		"*id:int": {},
		"@user->id:int!": {},
		"#likeable": {}
	}
}
```

## Nomenclature:

### Starting Symbols

- * : Represents a primary key constraint
- @ : Represents a foreign key constraint
- \# : Represents a polymorphic key constraint

### Terminal Symbols

- ? : Means the value can be NULL
- ! : Means the value must be unique
- + : Means the value can be unique and nullable

### Other Symbols

- -> : Identifies the foreign key target i.e. {table}->{attr}
- : : Identifies the type i.e. {attr_name}:{attr_type}
