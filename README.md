# Logitech M720 Button Configuration for Linux

This script can be used to configure mouse button mappings of a Logitech M720 mouse temporary.

The configuration is done via the HID++ protocol described in these documents:

 * [Logitech HID++2.0 Draft Specification](https://lekensteyn.nl/files/logitech/logitech_hidpp_2.0_specification_draft_2012-06-04.pdf)
 * [special keys and mouse buttons](https://lekensteyn.nl/files/logitech/x1b04_specialkeysmsebuttons.html#divertedButtonsEvent)

This script is created for personal use only and may or may not work for your device. Use at your own risk.

# How to Use

## Installation

Clone the repository and install this package with pip:

```
$ pip install --user -e /path/to/logitech-m720-config
```

## Run the script

This script will map `Button 8` on the thumb button by default.

Run in a terminal:

```
$ m720-config
```

## Create your own configuration

Tweak the source code in `m720_config/__init__.py` to adjust the configuration.

## Check your configuration

Use `xev | grep button` to monitor your changes to your mouse button mapping.

# How to Get Gestures On Linux?

You can use [Easystroke](https://github.com/thjaeger/easystroke/wiki) to add gesture support to your mouse. Use the thumb button as your gesture button and the behavior should be similar to that created by Logitech Options.
