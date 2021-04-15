
"""
All styles for the tkinter widgets are stored here.
Why this and not ttk Styles? There are no ttk styles for
canvas objects. Using the same method to stylize everything
feels correct to me.
"""

##################### fonts ################

helvetica20 = ["Helvetica", 20]
helvetica14 = ["Helvetica", 14]
helvetica10 = ["Helvetica", 10]

#################### widget styles #######################

grey0Frame = {
		"background": "#aaa"
		}

grey1Frame = {
		"background": "#494949"
		}

grey2Frame = {
		"background": "#333"
		}

grey1Label = {
		"background": "#494949",
		"foreground": "#eee",
		"font": helvetica14
		}

grey1BigLabel = {
		"background": "#494949",
		"foreground": "#eee",
		"font": helvetica20
		}

grey1Button = {
		"background": "#666",
		"foreground": "#eee",
		"activebackground": "#777",
		"activeforeground": "#eee",
		"highlightthickness": 1,
		"highlightbackground": "#666",
		"disabledforeground": "#444",
		"relief": "raised",
		"font": helvetica14,
		"cursor": "hand2"
		}

grey1SpinBox = {
		"background": "#666",
		"foreground": "#eee",
		"activebackground": "#777",
		"highlightthickness": 1,
		"highlightbackground": "#666",
		"relief": "raised",
		"buttoncursor": "hand2"
		}

scrollBar = {
		"background": "#eee",
		"highlightbackground": "#fff",
		"highlightcolor": "#000"
		}

scrollCanvas = {
		"background": "#494949",
		"highlightthickness": 0
		}

grey3Label = {
		"background": "#666",
		"foreground": "#eee",
		"font": helvetica14
		}

grey3bindBox = {
		"background": "#666"
		}

############# canvas object styles ########################

default = {
		"width": 3,
		"fill": "#000",
		"outline": "#111",
		"activefill": "#222", 
		"activeoutline": "#333"
		}

defaultLdotTextStyle = {
		"font": helvetica10,
		"fill": "#eee",
		"activefill": "#fff"
		}

defaultBarTextStyle = {
		"font": helvetica14,
		"fill": "#eee"
		}

selectedStyle = {
		"width": 3,
		"fill": "#99b",
		"outline": "#668",
		"activefill": "#aac",
		"activeoutline": "#779"
		}

selectedBarTextStyle = {
		"font": helvetica14,
		"fill": "#668"
		}

freeRouteNormal = {
		"width": 3,
		"fill": "#9b9",
		"outline": "#686",
		"activefill": "#aca",
		"activeoutline": "#797"
		}

freeRouteBarTextStyle = {
		"font": helvetica14,
		"fill": "#686"
		}

staticRouteNormal = {
		"width": 3,
		"fill": "#bb8",
		"outline": "#885",
		"activefill": "#cc9",
		"activeoutline": "#996"
		}

staticRouteBarTextStyle = {
		"font": helvetica14,
		"fill": "#885"
		}

circleRouteNormal = {
		"width": 3,
		"fill": "#b97",
		"outline": "#864",
		"activefill": "#ca8",
		"activeoutline": "#975"
		}

circleRouteBarTextStyle = {
		"font": helvetica14,
		"fill": "#864"
		}

straightRouteNormal = {
		"width": 3,
		"fill": "#b77",
		"outline": "#844",
		"activefill": "#c88",
		"activeoutline": "#955"
		}

straightRouteBarTextStyle = {
		"font": helvetica14,
		"fill": "#844"
		}

soundSourceNormal = {
		"width": 3,
		"fill": "#ccc",
		"outline": "#bbb",
		"activefill": "#eee",
		"activeoutline": "#ddd"
		}

soundSourceBarTextStyle = {
		"font": helvetica14,
		"fill": "#222"
		}

listenerNormal = {
		"width": 3,
		"fill": "#222",
		"outline": "#111",
		"activefill": "#333",
		"activeoutline": "#222"
		}

listenerBarTextStyle = {
		"font": helvetica14,
		"fill": "#ccc"
		}

dragDot = {
		"width": 2,
		"fill": "#a85",
		"outline": "#974",
		"activefill": "#b96",
		"activeoutline": "#a85"
		}

entryStyle = {
		"background": "#454545",
		"foreground": "#eee",
		"highlightthickness": 2,
		"highlightbackground": "#404040",
		"highlightcolor": "#353535",
		"insertbackground": "#ddd",
		"relief": "flat"
		}

damperDotStyle = {
		"width": 0,
		"fill": "#9b9"
		}
