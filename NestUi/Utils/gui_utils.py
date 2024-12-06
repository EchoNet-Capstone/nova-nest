from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu


'''
options_dict element format:
	{option_key: (QAction, <slot_func | None>),
	 ...,
	 last_option_key: "", 
	 'order': [option_1, 
	 		   option_2, 
			   ..., 
			   option_n]
	 }

	dict value is a tuple containing a QAction and either a function pointer to the 
	slot function on trigger or None (don't connect trigger)

	value of key 'order' contains the order of menu options, described by the key in the
	dict. a key not in the dict will be treated as a separator


'''
def add_menu_options(menu: QMenu, options: dict):
	for key in options['order']:
		try:
			curr_val = options[key]

			curr_action:QAction = curr_val[0]
			action_slot = curr_val[1]
			
			if action_slot:
				curr_action.triggered.connect(action_slot)

			menu.addAction(curr_action)
		except KeyError:	# separator
			menu.addSeparator()