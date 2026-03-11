extends Control

var db : SQLite = null

var selected_cols = ["id"]
var booster = []
var current_card = 0

var thread : Thread = null

func get_common_list(set_id: String) -> Array:
	var res = db.select_rows("cards", "setID = '%s' AND rarity = 'Common' AND type = 'REG'" % set_id, selected_cols)
	return res
	
func get_uncommon_list(set_id: String) -> Array:
	var res = db.select_rows("cards", "setID = '%s' AND rarity = 'Uncommon'" % set_id, selected_cols)
	return res
	
func get_rare_list(set_id: String) -> Array:
	var res = db.select_rows("cards", "setID = '%s' AND rarity = 'Rare'" % set_id, selected_cols)
	return res

func get_epic_list(set_id: String) -> Array:
	var res = db.select_rows("cards", "setID = '%s' AND rarity = 'Epic'" % set_id, selected_cols)
	return res

func get_alt_list(set_id: String) -> Array:
	var res = db.select_rows("cards", "setID = '%s' AND type = 'ALT'" % set_id, selected_cols)
	return res

func get_over_list(set_id: String) -> Array:
	var res = db.select_rows("cards", "setID = '%s' AND type = 'OVR'" % set_id, selected_cols)
	return res

func get_signed_list(set_id: String) -> Array:
	var res = db.select_rows("cards", "setID = '%s' AND type = 'SGN'" % set_id, selected_cols)
	return res

func get_token_list(set_id: String) -> Array:
	var res = db.select_rows("cards", "setID = '%s' AND type = 'TKN'" % set_id, selected_cols)
	return res

func gen_booster(set_id : String):
	
	var commons = pick_count(get_common_list(set_id),7)
	var uncommons = pick_count(get_uncommon_list(set_id),3)
	
	var flex_list = pick_count(get_uncommon_list(set_id),3) + pick_count(get_rare_list(set_id),1)
	flex_list.shuffle()
	var flex = [flex_list.pop_back()]
	
	var epic = randi_range(0,3) == 0
	var alt = randi_range(0,11) == 0
	var over = randi_range(0,71) == 0
	var signed = randi_range(0,719) == 0
	
	var special: Array = []
	if epic:
		special += pick_count(get_epic_list(set_id),1)
	if alt:
		special += pick_count(get_alt_list(set_id),1)
	if over:
		special += pick_count(get_over_list(set_id),1)
	if signed:
		special += pick_count(get_signed_list(set_id),1)
	
	var rares = pick_count(get_rare_list(set_id), 2 - len(special)) + special
	
	var token = pick_count(get_token_list(set_id),1)

	
	return commons + uncommons + flex + rares + token

func pick_count(cards : Array, count : int) -> Array:
	if count <0:
		return []
	cards.shuffle()
	return cards.slice(0,count)

func increment_display():
	var path = "cache/%s.png" % booster[current_card]
	var image = Image.load_from_file(path)
	$CenterContainer/TextureRect.texture = ImageTexture.create_from_image(image)
	current_card+=1

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	db = SQLite.new()
	db.path = "res://cards.db"
	db.open_db()
	booster = gen_booster("OGN")
	booster = booster.map(func(elem): return elem["id"])
	print(booster)

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass
