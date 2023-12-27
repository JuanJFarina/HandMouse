# HandMouse

This application uses your webcam to detect hand gestures and allow you to make the next 
mouse actions without the need to actually have a mouse:

- Mouse Movement (by having your hand open with your index finger raised above)
- Left Click (from the previous position, touch your middle finger tip with your thumb)
- Drag and Drop (similar to the previous, but hold the position)
- Right Click (similar to left click but using your ring finger with your thumb)

Once the application starts it will also use your microphone to detect three command
voices:

- Stop: for stopping the tracking of your hands
- Start: for tracking again
- Exit: for exiting the application

## Running the Python Code

Having python and pipenv installed, you can clone this repo and run the commands:

`
pipenv install dev

pipenv run serve
`

To start the application.

## Running the Executable

You can also download the .exe file from the release section and simply execute it.

Bear in mind that in doing so, your antivirus softwares will likely detect is as malware.