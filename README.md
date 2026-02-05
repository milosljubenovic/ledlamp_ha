# LED LAMP

Home Assistant custom integration for LED LAMP devices controlled by the MohuanLED app over Bluetooth LE.

https://play.google.com/store/apps/details?id=com.ledlamp&hl=en_US


I figured it should be pretty easy to get them working, and it was.  I have no intention of adding this to HACS in any official capacity, but it should work when you add this repo as a custom repo in HACS.

There are some btsnoop HCI logs in the `bt_snoops` folder if you want to examine them.

## Bluetooth LE commands

`7b ff 07 00 00 ff 00 ff bf`                 - On
`7b ff 07 00 00 00 00 ff bf`                 - Off

# Payload Structure Breakdown

| Byte Offset | Byte Value(s) | Explanation                                                                                                                                                             |
| ----------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0-3         | `7bff`        | **Static Prefix**: This part of the payload is constant and likely signifies the start of a control command.                                                            |
| 4-5         | `07`          | **Mode Identifier**: This byte seems to indicate the control mode, typically related to color or brightness.                                                            |
| 6-7         | `ff`          | **Intensity/Effect Modifier**: This byte often relates to the intensity or effect within the mode, but may not directly control brightness when scaling the RGB values. |
| 8-9         | `XX`          | **Red (R) Channel**: This byte represents the intensity of the red color in the RGB model. It is scaled according to the brightness level.                              |
| 10-11       | `XX`          | **Green (G) Channel**: This byte represents the intensity of the green color in the RGB model. It is scaled according to the brightness level.                          |
| 12-13       | `XX`          | **Blue (B) Channel**: This byte represents the intensity of the blue color in the RGB model. It is scaled according to the brightness level.                            |
| 14-15       | `00`          | **Control Padding**: This byte appears to be fixed and acts as padding, likely unrelated to color or brightness.                                                        |
| 16-17       | `ff`          | **Control Byte**: This byte seems related to finalizing the color or effect, often seen as constant but possibly involved in handling effect transitions.               |
| 18-19       | `bf`          | **Static Suffix**: The command ends with this static value, which likely signifies the end of the command.                                                              |

# Payload Example Breakdown

### Example 1: Full Brightness (RGB: Red `ff0000`, Brightness: 100%)

- **Payload**: `7bff07ffff0000ffbf`

| Byte Offset | Byte Value | Meaning              |
| ----------- | ---------- | -------------------- |
| 0-3         | `7bff`     | Static Prefix        |
| 4-5         | `07`       | Mode Identifier      |
| 6-7         | `ff`       | Intensity Modifier   |
| 8-9         | `ff`       | Red Channel (full)   |
| 10-11       | `00`       | Green Channel (none) |
| 12-13       | `00`       | Blue Channel (none)  |
| 14-15       | `00`       | Control Padding      |
| 16-17       | `ff`       | Control Byte         |
| 18-19       | `bf`       | Static Suffix        |

### Example 2: 50% Brightness (RGB: Green `00ff00`, Brightness: 50%)

- **Payload**: `7bff0780008000ffbf`

| Byte Offset | Byte Value | Meaning                    |
| ----------- | ---------- | -------------------------- |
| 0-3         | `7bff`     | Static Prefix              |
| 4-5         | `07`       | Mode Identifier            |
| 6-7         | `80`       | Intensity Modifier (50%)   |
| 8-9         | `00`       | Red Channel (none)         |
| 10-11       | `80`       | Green Channel (50% scaled) |
| 12-13       | `00`       | Blue Channel (none)        |
| 14-15       | `00`       | Control Padding            |
| 16-17       | `ff`       | Control Byte               |
| 18-19       | `bf`       | Static Suffix              |

### Example 3: 10% Brightness (RGB: Blue `0000ff`, Brightness: 10%)

- **Payload**: `7bff07330333ffbf`

| Byte Offset | Byte Value | Meaning                   |
| ----------- | ---------- | ------------------------- |
| 0-3         | `7bff`     | Static Prefix             |
| 4-5         | `07`       | Mode Identifier           |
| 6-7         | `33`       | Intensity Modifier (10%)  |
| 8-9         | `00`       | Red Channel (none)        |
| 10-11       | `00`       | Green Channel (none)      |
| 12-13       | `33`       | Blue Channel (10% scaled) |
| 14-15       | `00`       | Control Padding           |
| 16-17       | `ff`       | Control Byte              |
| 18-19       | `bf`       | Static Suffix             |

# Summary

- **Prefix** (`7bff`): Always static and signals the beginning of the payload.
- **Mode Identifier** (`07`): Identifies the operation mode (RGB color control in this case).
- **RGB Channels**: Bytes at positions 8-13 represent the RGB values, which are scaled according to brightness.
- **Suffix** (`bf`): The static ending that likely completes the command.
## Supported Features in this integration

- On/Off
- RGB colour
- Brightness (see known issues)
- Fancy colour Modes (not speed)
- Automatic discovery of supported devices

## Not supported and not planned

- Microphone interactivity
- Timer / Clock functions
- Discovery of current light state

The timer/clock functions are understandable from the HCI Bluetooth logs but adding that functionality seems pointless and I don't think Home Assistant would support it any way.

The discovery of the light's state requires that the device be able to tell us what state it is in.  The BT controller on the device does report that it has `notify` capabilities but I have not been able to get it to report anything at all.  Perhaps you will have more luck.  Until this is solved, we have to use these lights in `optimistic` mode and assume everything just worked.  Looking at HCI logs from the Android app it doesn't even try to enable notifications and never receives a packet from the light.

## Known Issues

- Brightness handling is very basic.  Brightness is handled by scaling the colour values.  Changing the brightness while an effect is showing will stop the effect.  This should be easy enough to fix, just I haven't done it yet.

## Installation

### Requirements

You need to have the bluetooth component configured and working in Home Assistant in order to use this integration.

### HACS

Add this repo to HACS as a custom repo.  Click through:

- HACS -> Integrations -> Top right menu -> Custom Repositories
- Paste the Github URL to this repo in to the Repository box
- Choose category `Integration`
- Click Add
- Restart Home Assistant
- LEDDMX devices should start to appear in your Integrations page

## Credits

This integration was possible thanks to the work done by raulgbcr in this repo:

<https://github.com/raulgbcr/lednetwf_ble>

which in turn is thanks to:

<https://github.com/dave-code-ruiz/elkbledom> for most of the base code adapted to this integration.

## Other projects that might be of interest

- [iDotMatrix](https://github.com/8none1/idotmatrix)
- [Zengge LEDnet WF](https://github.com/8none1/zengge_lednetwf)
- [iDealLED](https://github.com/8none1/idealLED)
- [BJ_LED](https://github.com/8none1/bj_led)
- [ELK BLEDOB](https://github.com/8none1/elk-bledob)
- [HiLighting LED](https://github.com/8none1/hilighting_homeassistant)
- [BLELED LED Lamp](https://github.com/8none1/ledble-ledlamp)
