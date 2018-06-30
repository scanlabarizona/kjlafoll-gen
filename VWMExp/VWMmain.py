#Author - Kyle J. LaFollette
#Correspondence - kjlafoll@umich.edu
#VWMmain.py
#--------------------
#A prime-probe visual working memory task


#SETUP
#////////////////////////////////////////////////

#IMPORT PACKAGES (*** When writing in Python, you'll want to install libraries. Libraries contain built-in modules that provide a whole system of prepared functions. If I want to get a list of numbers under a random distribution for example, I don't need to write a fuction for that - All that I need to do is use numpy.random.normal(). To access this funtion, I can either install numpy and call numpy.random.normal(), or be more specific and install numpy.random. To make calling easier, I can install a library 'as' something, such as 'install numpy as np'. Then, when I call a function from numpy, I can use something like 'np.random.normal()'. Note that you'll need to install these libraries into your python distribution, like conda, before you can import them)
#--------------------
from psychopy import visual, core, data, logging, sound, event, gui, monitors, tools; from psychopy.constants import *; from pyglet.window import key; import sys; ipy_stdout = sys.stdout; from psychopy.iohub import launchHubServer, EventConstants; sys.stdout = ipy_stdout; import numpy as np; from numpy.random import random, randint, normal, shuffle; import random; import pandas as pd; from pandas import DataFrame, Series; import os; import pygame
#-------------------- *** You'll notice that the variable assignments 'ipy_stdout = sys.stdout' and 'sys.stdout = ipy_stdout' are not imports. Why are they here then? Unfortunately, iohub, which we'll be using to track sustained key presses (for rotating stimuli), tries to redirect stdout when imported. iPython already 'wants' to redirect stdout, and if I were to omit this variable assignment, iPython and iohub would be in conflict. To preserve iPython functionality, I create a variable 'ipy_stdout' to represent stdout's current assignment to iPython, and after I import iohub, I ensure that control stays with iPython via 'sys.stdout = ipy_stdout'.


#SET UP IO KEYBOARD - maintains sustained key presses
#--------------------
io = launchHubServer(experiment_code = 'key_evts', psychopy_monitor_name = 'default') #This starts the iohub process for tracking sustained key presses. The return variable is used during the task to control iohub and maintain iohub devices.
global keyboard
keyboard = io.devices.keyboard #iohub creates a keyboard device by default. This variable will represent that keyboard device.
#--------------------

#PATH (*** Just as a precaution, we want to ensure that the relative path of files that we will be reading and outputting is from the same directory as this script)
#--------------------
_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)
#--------------------







#VARIABLE ASSIGNMENT
#////////////////////////////////////////////////

#CONSTANT VARIABLES - adjust sizing, coloring, and timing (*** We want to create some variables that can be readily adjusted. Constants such as the sizing of font, the radious of our grating stimuli, and the duration of the delay period are subject to change from iteration to iteration of the experiment, and so they should be easily identifiable and accessable)
#--------------------
MonitorSize = [1280,800]; MonitorWidth = 50; MonitorDist = 55; WindowSize = (1200, 900) #Monitor Settings. Note that this is not the window encompassing the experiment. I'm assigning these variables simply to have this information on hand in case I need it.
InstructionFont = u'Arial'; InstructionColor = '#ffffff'; NormalSize = 1; TutorialSize = .75; FixationSize = .5; CueColor = '#00ff00'; RewardSize = 7; FeedbackSize = 4 #For general font size and color, tutorial font, size and color of fixation diamond; reward font, and feedback font. Sizes will refer to the height of the text in inches when we use them as arguments in text stimuli.
GratingSize = 12; DistfromCenter = 9 #For size of gratings in centimeters and for establishing the their distance away from the center of the screen, also in centimeters.
BaseFixationPeriod = 1; SamplePeriod = 1; RewardPeriod = 2; TestPeriod = 3; FeedbackPeriod = 2; Delay = 8 #For the periods of time that the starting fixation, primes, reward/loss display, probe, feedback displays, and delay are presented (in seconds).
#--------------------

#MISCELLANEOUS CONSTANT VARIABLES (*** All of the following variables are meaningless on the own; they merely represent values that will be useful when checking whether some conditional is met during the experimental procedure).
#--------------------
MaxError = 20 #This represents the maximum error in degrees that a subject can have calibrated following training. This is important, so that subjects who peform VERY poorly, or who do not understand the task, during training, cannot "cheat" the accuracy determination in the experimental blocks.
BlockSize = 25 #This chuncks the spreadsheet containing our trial-by-trial variables into blocks of 25. Keeping this at 25 ensures that the program inserts a 'Something Block # Something' screen between every 25 trials.
TutorialDisable = 0 #If 0: Include tutorial instance, If 1: Exclude tutorial instance. Change to 1 only when debugging. Implimenting 'killswitches' like this are especially useful if you anticipate that a future iteration of your experiment will require that a section is omitted.
Codelock = 0 #Some screens that indicate the start of a new block are 'locked' so that participants cannot accidently continue on before key instructions are delivered. Pressing 'p' on these screens bypasses the lock. Keeping this at 0 ensures that not all text boxes are locked.
#--------------------

#EXPERIMENT INFORMATION
#--------------------
Iteration = int(raw_input("Please enter experiment iteration - see protocol: ")) #This will ask that you input the iteration number of the experiment into the terminal before the experiment begins, and will assign that number to an 'Iteration' variable. This variable will be essential for determining which conditionals are met during the experimental procedure, and the meeting of those condtionals is the distinction between one iteration's procedure and that of another iteration's.
Participant = int(raw_input("Please enter subject number: ")) #Like the above variable assignment, this will ask for an input into the terminal, and will assign that input to the 'Participant' variable. This won't be as useful as 'Iteration', but we will use it to record the subject number in the output file (containing our data), and for naming the output file.
Condition = int(raw_input("Please enter condition: ")) #One last input; we'll be assigning this in front of our participants, so we'll have to code for conditions instead of inputting them explicitly.
if Iteration == 1:
    Condition = 'gain'
elif Iteration == 2:
    if Condition == 1:
        Condition = 'Pressure'
    elif Condition == 2:
        Condition = 'Control'
elif Iteration == 3:
    Condition = 'loss'
FileName = "data/%s_VWMInt_output.csv" % Participant #This is important - we need to have a string ready indicating the name of the file that we're going to be outputting, containing our participant's data. Also note that we included '%s' and '% Participant' in the string. This replaces %s with our Participant value, ensuring that the appropriate file name is included on our output.

#GLOBAL STARTING VALUES & LISTS (*** We're going to be calling these variables as conditionals and appending these lists throughout the experiment, so let's assign them all now, keeping them in one place in case we need to identify them later. You'll find most of these variables in our 'Trial()' function)
#--------------------
t = 0; RT = 0; fixationperiod = 0; BlockNum = 0; TotalACC = 0; resp = event.BuilderKeyResponse(); fixationseq = 1; TrainingDisable = 0; CurrentPos = 0; TutorialPos = 0; StartingTrial = 0; FeedbackInit = 0
CuedOrientation = []; FakeOrientation = []; CuedHemisphere = []; AverageMarginError = []; DeviationfromCued = []; DeviationfromNonCued = []; TrialReward = []; TrialMarginError = []; TrialRT = []; TrialAcc = []; FinalOri = []; BlockNumber = []; MaxErrorPerm = []; ParticipantID = []; ConditionList = []; TrialMarginErrorNonCued = []; CuedOrientationNonJittered = []; Jitter = []; FakeOrientationNonJittered = []; IterationList = []; ProbeOriList = []; RotList = []; ShootDistList = []
col1 = 'MaxErrorPermit'; col2 = 'CuedOrientation'; col3 = 'FakeOrientation'; col4 = 'CuedHemisphere'; col5 = 'AverageMarginError'; col6 = 'ProbeDeviationfromCued'; col7 = 'ProbeDeviationfromNonCued'; col8 = 'TrialReward'; col9 = 'TrialMarginError'; col10 = 'TrialRT'; col11 = 'TrialAcc'; col12 = 'FinalOri'; col13 = 'BlockNumber'; col14 = 'ParticipantID'; col15 = 'Condition'; col16 = 'TrialMarginErrorNonCued'; col17 = 'CuedOrientationNonJittered'; col18 = 'Jitter'; col19 = 'FakeOrientationNonJittered'; col20 = 'Iteration'; col21 = 'ProbeOri'; col22 = 'RotationDir'; col23 = 'FinalDeviationfromCued'
#--------------------







#OBJECT ASSIGNMENT
#////////////////////////////////////////////////

#MONITOR AND WINDOW COMPONENTS (*** Throughout the experiment, we will be drawing objects onto a window object. We'll call this window object 'win', and we'll format that object with arguments to adjust the window to our needs. For instance, we don't want our window to be full screen, so we set fullscr to False. You'll notice that we also have to include an argument for the monitor of which our window will reside. We'll call that monitor object 'mon', and adjust it via the constant variables that we created earlier).
#--------------------
mon = monitors.Monitor('expMonitor', width = MonitorWidth, distance = MonitorDist)
mon.setSizePix(MonitorSize)
mon.saveMon()
win = visual.Window(size=WindowSize, fullscr=False, screen=0, allowGUI=False, allowStencil=False, monitor='expMonitor', color=[0, 0, 0], colorSpace='rgb', blendMode='avg', useFBO=True, units='cm')
#--------------------

#TEXT BASED COMPONENTS
#--------------------
InstructionTxt = open("VWM_instructions_it%s.txt" % Iteration) #This imports a .txt file (specifically, one that contains our text for the introductory instructions screen) and assigns it to an object, which we'll call 'InstructionTxt'. This object is not in printable condition yet, so we'll have to fix that.
lines = InstructionTxt.readlines() #Let's fix that. This organizes object into a readable series of strings. Strings are a very popular type in Python.
TextBox = visual.TextStim(win=win, ori=0, name='IntroInstruction', text  = ' '.join(str(x) for x in lines),font=InstructionFont, units = 'cm', pos=[0, 0], height=NormalSize, wrapWidth=40, color = InstructionColor, colorSpace='rgb', opacity=1) #This sets up a text stimulus that will be used for all text displays in the experiment. New text stims will not be created in this experiment, rather, the arguments of this object will be adjusted regularly to fit our text display needs. As it is written above, the text stim is currently prepared to read in 'lines'. First, we ensure that 'lines' is of the string type with str(), and then we join those lines togeter with join() to make them one printable string. Normally, this long string would fly off of the window when drawn, but if you take a look at the .txt file itself, you notice some '\n' symbols - these, when read in, represent a line break, keeping our text from continuing on beyond the width of our window.
Reward    = visual.TextStim(win=win, ori=0, name='Reward', text  = u'replace during prep', font=InstructionFont, units = 'cm', pos=[0, 0], height=RewardSize, wrapWidth=40, color = InstructionColor, colorSpace='rgb', opacity=1)
#--------------------

#GRATING STIMULI COMPONENTS
#--------------------
Sample = visual.GratingStim(win, sf = 1, size = GratingSize, mask = 'circle', units = 'cm') #This object will represent the cued stimulus. Note that the argument 'mask' represents the shape of the grating.
FSample = visual.GratingStim(win, sf = 1, size = GratingSize, mask = 'circle', units = 'cm') #This object will represent the fake, or non-cued stimulus. Why not use the 'Sample' object for representing all gratings, as we're doing with the 'TextBox' object for text displays? This issue is that multiple gratings need to be displayed as once - you can't have the same object be in two places at once, can you? So, we create a second object to represent the second grating.
Masks = visual.ElementArrayStim(win, nElements = 4, elementTex = 'sqr', units = 'cm', colors = '#333333', elementMask = 'circle', oris = [0,0,90,90], xys = [[-DistfromCenter, 0 ], [DistfromCenter, 0], [-DistfromCenter, 0], [DistfromCenter, 0]], opacities = .5, sizes = GratingSize) #We want to create some Masks to prevent participants from using residual imagery as a substitute for working memory during the delay period. An element array stimulus will serve the purpose of creating two masks. But wait! - why didn't we use this function to create two sample stimuli / primes? You could actually do this! Rather than manipulate the orientation of Sample and FSample individually, you can manipulate the 'oris' set in an elemental array. I created two separate sample stimuli simply due to preference. Also note that this Element array has '4' elements, composing 2 masks. Why is this? - you'll notice that each element has opacity of .5, making them transparent. All we are doing is overlapping two transparent grating stimuli to the left of the screen, and two to the right, resulting in two  "grid-like" masks. 
#--------------------

#FIXATION DIAMOND COMPONENTS (*** the fixation 'diamond' is really just two triangles presented side-by-side. We will position these triangles as close together as possible in the center of the screen and orient them in opposite directions to give the illusion of a diamond. Why not just make a diamond? - We will be cueing participants to the left or right stimuli via a green arrow within the diamond; making each side of the diamond a triangle simplifies the process of cueing, as all we'll need to do is change the fill color of one of the triangles, and return it to its original color at the end of cueing.)
#--------------------
FixationLeft = visual.Polygon(win = win, edges = 3, radius = FixationSize, fillColor = InstructionColor, ori = -90, pos = [-.27,0], units = 'cm')
FixationRight = visual.Polygon(win = win, edges = 3, radius = FixationSize, fillColor = InstructionColor, ori = 90, pos = [.27,0], units = 'cm')
#--------------------

#MISCELLANEOUS COMPONENTS
#--------------------
ScreenClock = core.Clock() # We're going to want to set some time limits for meeting conditionals, so we'll create an object the represents the core system's internal clock.
#NOTE - did not include OriChecklist
#--------------------







#MAIN AND TRIAL FUNCTIONS
#////////////////////////////////////////////////

#MAIN FUNCTION (*** This will be tough to digest, so I've chunked it into sections. Note that each section is still a part of the main() function.)
#--------------------
def main():
    global BlockNum, TrainingDisable, MaxError, CurrentPos, TutorialDisable, StartingTrial, FeedbackInit, TrialReward, TrialAcc, Codelock #Functions keep variables local, meaning that the variables used by the function are kept isolated from other functions. There are certain variables that we'd like to update and call across functions, so we'll have to work around this. To do this, I'll make those variables that I'd like to share across function global. I'll make sure of this by using 'global' before on each variable at the start of the function.
    TrialNum = 0 #A marker to remember what trial we're on.
    SetTrainingSchedule() #See this function in 'Supporting Functions' for details. Essentially, here we are importing a permutation of a schedule of training trials from a csv.
    for x in range(StartingTrial, len(TrainingSchedule) + 1): #The bread and butter of this function. main() will repeat for each value of x in the range, customizing each trial according to the current x value. Starting trial is at 0, and the length of the imported training schedule is 50. The last number in a range is non-inclusive, so we'll want to add 1 to this so that we loop through all 50 training trials.
#TUTORIAL
#--------------------
        if x == 0: #The tutorial section of the experiment will only take place on the first "trial". It will never occur after x>0
            TextBox.text = ' '.join(str(x) for x in lines) #Remember how we organized lines into a series of strings? We need to join those strings together if we want the text attribute of TextBox to be readable.
            DispText() #See function DispText() below. 
            if TutorialDisable == 0: #If tutorial is to be included, do the following
                for x in range(0,4): #run through this 3 times
                    Trial() #See function Trial()
                    CurrentPos = CurrentPos + 1 #We've already set this variable to 0 earlier, so now we're moving it up 1. This variable refers to the row from our training schedule csv that we'll be pulling stimulus parameters from. We want each trial to have certain distinctions from one another, but we don't want those distinctions to be determined randomly. That's why we prearrange those distinctions in our schedule csv. Distinctions like angle of the prime, which prime will be cued, etc. CurrentPos makes sure that we go through each of those prearanged distinctions.
            TutorialDisable = 1 #We're done with the tutorial trials, so let's disable them, as future checks will look to see whether we're in the tutorial phase.
#--------------------

#TRAINING BLOCK(S)
#--------------------           
            TextBox.pos = [0,0]; TextBox.wrapWidth = 30; TextBox.height=NormalSize #Center the text object, keep the line width within the window boundaries, and set the text size to one of our variables.
            TextBox.text = u'Training Block # 1 \nThe following series of trials will be for training purposes only. Continue with the experiment when ready. Try to keep the gratings in your minds eye (visualize them) for the best effect.' #Assign new text for the training block. The \n represents a line break.
            DispText()
            BlockNum = "Training" #When organizing by block number in our output, we'll note that this "block" was the training block.
            SetTrainingSchedule() #See function SetTrainingSchedule()
            CurrentPos = 0 #Why are we setting the position back to 0? Didn't we want to go through each prearranged trial no more than once? Well, the tutorial had us run through 3 of our training trials already, but we still want to include those in training. To do this, we reshuffle the training schedule with the above function, and then we start back at row 0, hense this reset.
        elif x >= 1: #Trial 1, the first of the non-tutorial trials.
            if TrialNum == (BlockSize - 1): #Check to see if this is the last trial in the block. Remember that BlockSize starts at 0, and that the last number in a range is non-inclusive, hense the "-1".
                FeedbackInit = 1 #If this is indeed the last trial in the block, we want to set this variable to 1, so that when we check whether we should present a feedback screen (see Trial() function), we do so.
            if TrialNum >= BlockSize: #Once we've completed all of the trial in a block (met the total number of trials required of a block), do the following
                TrialNum = 0 #Set this variable back to 0, so that we can go through the loop again on subsequent blocks.
                if Iteration != 2:
                    TextBox.text = u'Training Block # 2 \nContinue with the experiment when ready.'
                elif Iteration == 2:
                    TextBox.text = u'Experimental Block # 1 \nPlease notify the experimenter before continuing.' #TextBox will be locked and will require that the experimenter press the appropriate lock key
                    Codelock = 1
                    BlockNum = 1
                DispText()
            if TrialNum == (BlockSize - 1):
                FeedbackInit = 1 #Check again whether we should be prepared to show a feedback screen
            Trial() #This is the most important function. Now that we've checked to see what kind of trial we're doing and where it is in the schedule, it's time to start the trial. See the Trial() function below.
            MaxError = sum(TrialMarginError) / float(len(TrialMarginError)) #This variable records the average margin of error across trials in the training block
            if MaxError > 45:
                MaxError = 45 #We don't want to inflate our standardized scores in the experimental blocks because of some astronomical failures in the training block. If the participant was worse than 45 degrees off the mark on average, just set their average to 45.
            CurrentPos = CurrentPos + 1
            TrialNum = TrialNum + 1 #Let's set the marker indicating the current trial up by 1, and begin this loop anew.
#--------------------

#EXPERIMENTAL BLOCKS
#--------------------   
    TrainingDisable = 1 #A marker to indicate that we are no longer in the training block.
    SetBlockSchedule() #Like SetTrainingSchedule(), this arranges our block schedule .csv into a permutation of the original row-wise. See the function below.
    StartingTrial = 0 #See the next "for" loop below. This is just to add flexibility in debugging.
    CurrentPos = 0 #We're starting a new schedule, so we want to be back on row 1.
    BlockNum = 0 #First experimental block.
    TrialNum = BlockSize + 1 #This might seem strange, but we want the next loop to think that we are beginning at the end of a block, so that our next experimental trial will be from a new (which is our first) experimental block. So, we'll say that our current trial number exceeds the block size, and the loop below will act accordingly.
    for x in range(StartingTrial, len(BlockSchedule)):
        if TrialNum == (BlockSize - 1):
            FeedbackInit = 1
        if TrialNum >= BlockSize: #Remember that weird value setting we did with TrialNum 4 lines above? Now it'll come into use.
            TrialNum = 0
            BlockNum = BlockNum + 1
            if BlockNum == 1: #All of the various information that we present via text at the start of the first experimental block, contingent on iteration and condition.
                if Iteration == 0 or Iteration == 1:
                    TextBox.text = u'Experimental Block # %r \nEach trial will now be worth a predetermined amount of money. At the conclusion of this experiment, one trial will be selected at random, and if you were successful on that trial, you will earn that trial\'s worth of money. To improve your odds of earning, try to respond as accurately as possible on every trial.' % BlockNum
                elif Iteration == 2:
                    BlockNum = BlockNum + 1
                    if Condition == 'Pressure':
                        TextBox.text = u'Performance Calibrated: You HAVE NOT improved your average accuracy by 15%'
                        Codelock = 1
                    elif Condition == 'Control':
                        TextBox.text = u'Performance Calibrated: You HAVE improved your average accuracy by 5%'
                        Codelock = 1
                    TextBox.text = u'Experimental Block # %r \nPlease notify the experimentor before continuing for a performance review.' % BlockNum
                    Codelock = 1
                elif Iteration == 3:
                    TextBox.text = u'Experimental Block # %r \nEach trial will now be associated with a predetermined loss. At the conclusion of this experiment, one trial will be selected at random, and if you were to fail on that trial, you will lose that trial\'s worth of money. To improve your odds of not losing, try to respond as accurately as possible on every trial.' % BlockNum
            else:
                TextBox.text = u'Experimental Block # %r' % BlockNum #If this isn't the first experimental block, just set TextBox to this generic text.
            DispText()
        if TrialNum == (BlockSize - 1):
            FeedbackInit = 1
        Trial()
        TrialNum = TrialNum + 1
        CurrentPos = CurrentPos + 1
        #And that's the end of our experimental blocks!!!
    if Iteration == 0 or Iteration == 1: #In iterations 0 and 1, we want to show subjects whether they were accurate enough on their randomly selected trial, for compensation purposes.
        SelectedTrial = random.randint(len(pd.read_csv('TrainingSchedule_it%s.csv' % Iteration,sep='\t')),len(pd.read_csv('data/%s_VWMInt_output.csv' % (ExpInfo['Participant']), sep= '\t'))-1) #Picks number representing a random trial from our output.
        print 'Trial # %s' % SelectedTrial
        print TrialReward[SelectedTrial] #Show the value of a variable (in this case, reward value) in our output associated with the selected trial
        if TrialAcc[SelectedTrial] == 1:
            print 'Correct!'
        else:
            print 'Incorrect'
    TextBox.text = u'You have completed the experiment. Please notify your experimenter.'
    DispText()
    core.quit() #YAY!
#--------------------
#--------------------

#TRIAL FUNCTION (*** This may look simple, but it is supported by many, many functions that are defined below it. Essentially, this function is responsible for the order in which we carry out the supporting function. Without those functions, there wouldn't be a trial. Given this, you'll need to refer to those functions later in this script to understand Trial(). Comments here will describe what the supporting functions do functionally, but you'll want to refer to those functions to see how they do what they do.)
#--------------------
def Trial():
    global fixationseq, TrainingDisable, FeedbackInit, TutorialPos, OriChecklist, FOriChecklist, OriChecklist2, FOriChecklist2
    if Iteration == 0 and TrainingDisable == 1 and BlockNum !="Training":
        StartReward() #Shows the reward associated with this trial
    if Iteration == 3 and TrainingDisable == 1 and BlockNum !="Training":
        StartReward()   
    fixationseq = 1 #This variable denotes what fixation cross is being presented. But aren't they all the same? No, there are timing differences between the first cross presented in a trial and the next. Fixation crosses that are displayed when fixationseq=1 are different from those being displayed when fixationseq=2
    StartFixation() #Shows the fixation cross.
    StartSample() #Shows the two primes
    OriChecklist = [Sample.ori,Sample.ori+180,Sample.ori-180,Sample.ori+360,Sample.ori-360] #This seems odd, but given that participants will be rotating our stimuli, and given that there aren't really any differences visually between gratings at 0 degrees, 180 degrees, and 360 degrees, we need to note that the orientation of our cued prime is the same even if you shift it 180 or 360 degrees. This list will record the acceptable orientations.
    FOriChecklist = [FSample.ori,FSample.ori+180,FSample.ori-180,FSample.ori+360,FSample.ori-360] #Same as above, but for our non-cued prime.
    if Iteration == 4:
        fixationseq = 1
    else:
        fixationseq = 2 # We want to use a different type of fixation cross, unless our Iteration is 4. This is because Iteration 4 contains 2 sets of primes per trial. See StartFixation() for distinctions.
    if Iteration == 1 and TrainingDisable == 1 and BlockNum !="Training":
        StartReward ()
    StartFixation()
    if Iteration == 4: #Same as before, but for our second set of primes, as is required in iteration 4. 
        StartSample()
        OriChecklist2 = [Sample.ori,Sample.ori+180,Sample.ori-180,Sample.ori+360,Sample.ori-360] 
        FOriChecklist2 = [FSample.ori,FSample.ori+180,FSample.ori-180,FSample.ori+360,FSample.ori-360]
        fixationseq = 2
        StartSetCue() #Cues either the first or second set of primes.
        StartFixation()
    StartTest() #Show the probe.
    if TutorialDisable == 1:
        CollectData() #If we're not in the tutorial phase, collect some data!
    else:
        DispTutorial()
        TutorialPos = TutorialPos + 1
    if FeedbackInit == 1: #If we're at the end of our block and we're ready to show feedback, do so, dependent on Iteration. Iteration 2 doesn't give any indication of performance.
        if Iteration == 0 or Iteration == 1 or Iteration == 3:
            TextBox.text = u'Your average error on this block was %r\xb0 . Remember to keep the gratings in your minds eye for the best effect.' % (sum(TrialMarginError[(len(TrialMarginError) - BlockSize):]) / float(BlockSize))
        elif Iteration == 2:
            TextBox.text = u'You have reached the end of this block. Please continue when ready. Remember to keep the gratings in your minds eye for the best effect.'
            DispText()
            FeedbackInit = 0 #We don't want to accidentally show feedback after the next trial!
#--------------------







#SUPPORTING FUNCTIONS
#////////////////////////////////////////////////

#TEXT DISPLAY PRESENTATION FUNCTION
#--------------------
def DispText():
    global Codelock
# Prepare for Instructions
    ScreenClock.reset()
    t                       = 0
    frameN                  = -1
    OK1                     = event.BuilderKeyResponse()
    OK1.status              = NOT_STARTED
    TextBox.status = NOT_STARTED
# Start Instructions
    continueRoutine = True
    while continueRoutine:
        t      = ScreenClock.getTime()
        frameN = frameN + 1
        if t >= 0.0 and TextBox.status == NOT_STARTED:
            TextBox.tStart      = t
            TextBox.frameNStart = frameN
            TextBox.setAutoDraw(True)
        if t >= 0.0 and OK1.status == NOT_STARTED:
            OK1.status = STARTED
            event.clearEvents(eventType ='keyboard')
        if OK1.status == STARTED:
            theseKeys = event.getKeys()
            if Codelock == 0:
                if len(theseKeys) > 0:
                    OK1.keys = theseKeys[-1]
                    TextBox.setAutoDraw(False)
                    continueRoutine = False
            elif Codelock == 1 and len(theseKeys) > 0:
                if theseKeys[0] == 'p': #the locked screen can be bypassed by the experimenter with the "p" key
                    TextBox.setAutoDraw(False)
                    Codelock = 0
                    continueRoutine = False
                else:
                    event.clearEvents(eventType ='keyboard')
        if continueRoutine:
            win.flip()
        if event.getKeys(keyList=["escape"]):
            win.close()
            core.quit()
#--------------------

#SET TRAINING SCHEDULE FUNCTION
#--------------------
def SetTrainingSchedule():
    global RewardSchedule, CuedOriSchedule, NonCuedOriSchedule, CuedHemiSchedule, DeviationSchedule, TrainingSchedule
    RewardSchedule = []
    CuedOriSchedule = []
    NonCuedOriSchedule = []
    CuedHemiSchedule = []
    DeviationSchedule = []
    TrainingSchedule = pd.read_csv("TrainingSchedule_it%s.csv" % Iteration)
    RandTrainingSchedule = TrainingSchedule.iloc[np.random.permutation(len(TrainingSchedule))]
    for x in range(len(RandTrainingSchedule.index)):
        RewardSchedule.append(RandTrainingSchedule.iloc[x][0])
        CuedOriSchedule.append(RandTrainingSchedule.iloc[x][1])
        NonCuedOriSchedule.append(RandTrainingSchedule.iloc[x][2])
        CuedHemiSchedule.append(RandTrainingSchedule.iloc[x][3])
        DeviationSchedule.append(RandTrainingSchedule.iloc[x][4])
#--------------------

#SET BLOCK SCHEDULE FUNCTION
#--------------------
def SetBlockSchedule():
    global RewardSchedule, CuedOriSchedule, NonCuedOriSchedule, CuedHemiSchedule, DeviationSchedule, BlockSchedule
    RewardSchedule = []
    CuedOriSchedule = []
    NonCuedOriSchedule = []
    CuedHemiSchedule = []
    DeviationSchedule = []
    BlockSchedule = pd.read_csv("BlockSchedule_it%s.csv" % Iteration)
    RandBlockSchedule = BlockSchedule.iloc[np.random.permutation(len(BlockSchedule))]
    for x in range(len(RandBlockSchedule.index)):
        RewardSchedule.append(RandBlockSchedule.iloc[x][0])
        CuedOriSchedule.append(RandBlockSchedule.iloc[x][1])
        NonCuedOriSchedule.append(RandBlockSchedule.iloc[x][2])
        CuedHemiSchedule.append(RandBlockSchedule.iloc[x][3])
        DeviationSchedule.append(RandBlockSchedule.iloc[x][4])
#--------------------

#REWARD PRESENTATION FUNCTION
#--------------------
def StartReward():
#Prepare for Reward
    global resp, RewardPeriod, TutorialPos
    ScreenClock.reset()
    t             = 0
    frameN        = -1
    Reward.text   = u'$%r' % RewardSchedule[CurrentPos]
    if Iteration == 1:
        RewardPeriod = 0
    Reward.status = NOT_STARTED
# Start Reward
    continueRoutine = True
    while continueRoutine:
        t = ScreenClock.getTime()
        frameN = frameN + 1
        if t >= 0.0 and Reward.status == NOT_STARTED:
            Reward.tStart      = t
            Reward.frameNStart = frameN
            Reward.setAutoDraw(True)
            Reward.status = STARTED
        if Reward.status == STARTED and t >= (0.0 + (RewardPeriod-win.monitorFramePeriod*0.75)):
            if Iteration == 0 or Iteration == 3:
                Reward.setAutoDraw(False)
            continueRoutine = False
        if continueRoutine:
            win.flip()
        if event.getKeys(keyList=["escape"]):
            win.close()
            core.quit()
#--------------------

#FIXATION PRESENTATION FUNCTION
#--------------------
def StartFixation():
# Prepare for Fixation
    global fixationseq, TutorialPos
    ScreenClock.reset()
    t      = 0
    frameN = -1
    if fixationseq == 1:
        fixationperiod = BaseFixationPeriod
    else:
        if TutorialDisable == 0 and TutorialPos < 5:
            fixationperiod = BaseFixationPeriod + 1
        else:
            fixationperiod = Delay
    FixationLeft.status = NOT_STARTED
    DrawLoop = NOT_STARTED
# Start Fixation
    continueRoutine = True
    while continueRoutine:
        t      = ScreenClock.getTime()
        frameN = frameN + 1
        if t >= 0.0 and FixationLeft.status == NOT_STARTED:
            FixationLeft.tStart      = t
            FixationLeft.frameNStart = frameN
            if fixationseq != 1:
                Masks.setAutoDraw(True)
            if fixationseq == 1 or Iteration == 0 or Iteration == 2 or Iteration == 3:
                FixationLeft.setAutoDraw(True)
                FixationRight.setAutoDraw(True)
                if TutorialDisable == 0:
                    t = 0
                    DispTutorial()
                    ScreenClock.reset()
                    t = ScreenClock.getTime(); TutorialPos = TutorialPos + 1
            FixationLeft.status = STARTED
        if t >= 0.0 and fixationseq !=1:
            if DrawLoop == NOT_STARTED:
                if Iteration == 1:
                    FixationLeft.setAutoDraw(True)
                    FixationRight.setAutoDraw(True)
                    if TutorialDisable == 0:
                        t = 0
                        DispTutorial()
                        ScreenClock.reset()
                        t = ScreenClock.getTime(); TutorialPos = TutorialPos + 1
                    Reward.setAutoDraw(False)
                if CuedHemiSchedule[CurrentPos] == 'right':
                    FixationRight.fillColor = CueColor
                    FixationRight.lineColor = CueColor
                    FixationLeft.fillColor = InstructionColor
                    FixationLeft.lineColor = InstructionColor
                elif CuedHemiSchedule[CurrentPos] == 'left':
                    FixationLeft.fillColor = CueColor
                    FixationLeft.lineColor = CueColor
                if TutorialDisable == 0:
                    t = 0
                    DispTutorial()
                    ScreenClock.reset()
                    t = ScreenClock.getTime(); TutorialPos = TutorialPos + 1
                DrawLoop = STARTED
        if t >= 1.0 and fixationseq !=1:
            Masks.setAutoDraw(False)
        if FixationLeft.status == STARTED and t >= (0.0 + (fixationperiod-win.monitorFramePeriod*0.75)) and Iteration !=4:
            if fixationseq == 1:
                FixationLeft.setAutoDraw(False)
                FixationRight.setAutoDraw(False)
                FixationLeft.fillColor = InstructionColor
                FixationLeft.lineColor = InstructionColor
                FixationRight.fillColor = InstructionColor
                FixationRight.lineColor = InstructionColor
            continueRoutine = False
        elif FixationLeft.status == STARTED and t >= (BaseFixationPeriod) and Iteration ==4:
            if fixationseq == 1:
                FixationLeft.setAutoDraw(False)
                FixationRight.setAutoDraw(False)
                FixationLeft.fillColor = InstructionColor
                FixationLeft.lineColor = InstructionColor
                FixationRight.fillColor = InstructionColor
                FixationRight.lineColor = InstructionColor
            continueRoutine = False
        if continueRoutine:
            win.flip()
        if event.getKeys(keyList=["escape"]):
            win.close()
            core.quit()
#--------------------

def StartSetCue():
    ScreenClock.reset()
    CuedSet = randint(1,2)
    TextBox.text = u'%s' % CuedSet
    TextBox.pos = [0,0]
    TextBox.setAutoDraw(True)
    t = ScreenClock.getTime()
    CueCheck = 0
    continueRoutine = True
    while continueRoutine:
        if t >= BaseFixationPeriod and CueCheck ==0:
            TextBox.setAutoDraw(False)
            FixationLeft.setAutoDraw(True)
            FixationRight.setAutoDraw(True)
            CueCheck = 1
            ScreenClock.reset()
            t = ScreenClock.getTime()
        if t >= Delay and CueCheck ==1:
            continueRoutine = False




#PRIME PRESENTATION FUNCTION
#--------------------
def StartSample():
#Prepare for Sample
    global resp, fixationseq, cuedhemi, TutorialPos, PrimeOri, FPrimeOri, JitterQuant
    ScreenClock.reset()
    t = 0
    frameN = -1
    if CuedHemiSchedule[CurrentPos] == 'left':
        cuedspace = -1
    elif CuedHemiSchedule[CurrentPos] == 'right':
        cuedspace = 1
    fixationseq = 2
    Sample.status = NOT_STARTED
    FSample.status = NOT_STARTED
#Start GratingSample
    continueRoutine = True
    while continueRoutine:
        t = ScreenClock.getTime()
        frameN = frameN + 1
        if t >= 0.0 and Sample.status == NOT_STARTED and FSample.status == NOT_STARTED:
            Sample.tStart = t
            FSample.tStart = t
            Sample.frameNStart = frameN
            FSample.frameNStart = frameN
            FixationLeft.setAutoDraw(True)
            FixationRight.setAutoDraw(True)
#Draw in to-be-cued stimulus
            JitterQuant = (np.random.randint(5,8) * np.random.choice([-1,1]))
            Sample.ori = CuedOriSchedule[CurrentPos] + JitterQuant
            PrimeOri = Sample.ori
            Sample.pos = [DistfromCenter*cuedspace,0]
            Sample.setAutoDraw(True)
            Sample.status = STARTED
#Draw in fake stimulus
            FSample.ori = NonCuedOriSchedule[CurrentPos] + (np.random.randint(5,8) * np.random.choice([-1,1]))
            FPrimeOri = FSample.ori
            FSample.pos = [-DistfromCenter*cuedspace,0]
            FSample.setAutoDraw(True)
            FSample.status = STARTED
            if TutorialDisable == 0:
                t = 0
                DispTutorial()
                ScreenClock.reset()
                t = ScreenClock.getTime(); TutorialPos = TutorialPos + 1
        if Sample.status == STARTED and FSample.status == STARTED and t >= (0.0 + (SamplePeriod-win.monitorFramePeriod*0.75)):
            Sample.setAutoDraw(False)
            FSample.setAutoDraw(False)
            FixationLeft.setAutoDraw(False)
            FixationRight.setAutoDraw(False)
            continueRoutine = False
        if continueRoutine:
            win.flip()
        if event.getKeys(keyList=["escape"]):
            win.close()
            core.quit()
#--------------------

#PROBE PRESENTATION FUNCTION
#--------------------
def StartTest():
#Prepare for Test
    global resp, RT, TutorialPos, FeedbackInit, TutorialDisable, TrainingDisable, ProbeOri, RotDir
    ScreenClock.reset()
    t = 0
    RT = 0
    frameN = -1
    Rotation = 0
    OK2                = event.BuilderKeyResponse()
    OK2.status         = NOT_STARTED
    Sample.status = NOT_STARTED
    FixationLeft.fillColor = InstructionColor
    FixationLeft.lineColor = InstructionColor
    FixationRight.fillColor = InstructionColor
    FixationRight.lineColor = InstructionColor
    keyboard.clearEvents()
# Start Test
    continueRoutine = True
    while continueRoutine:
        t = ScreenClock.getTime()
        frameN = frameN + 1
        if t >= 0.0 and Sample.status == NOT_STARTED:
            Sample.tStart = t
            Sample.frameNStart = frameN
            Sample.ori += DeviationSchedule[CurrentPos]
            ProbeOri = Sample.ori
            Sample.setAutoDraw(True)
            Sample.status = STARTED
            if TutorialDisable == 0:
                t = 0
                DispTutorial()
                ScreenClock.reset()
                t = ScreenClock.getTime(); TutorialPos = TutorialPos + 1
                TutorialDisable = 2
                Sample.setAutoDraw(False)
                FixationLeft.setAutoDraw(False)
                FixationRight.setAutoDraw(False)
                continueRoutine = False
        if t >= 0.0 and OK2.status == NOT_STARTED:
            OK2.status = STARTED
        if OK2.status == STARTED:
            for evt in keyboard.getEvents():
                if evt.type == EventConstants.KEYBOARD_PRESS and Rotation == 0:
                    if evt.key == u'left' and evt.key != u'right':
                        Rotation = -2
                        keyboard.clearEvents()
                    elif evt.key == u'right' and evt.key != u'left':
                        Rotation = 2
                        keyboard.clearEvents()
                    elif evt.key == u'up':
                        RT = t
                        Sample.setAutoDraw(False)
                        if any(Sample.ori >= x - MaxError and Sample.ori <= x + MaxError for x in OriChecklist):
                            resp.corr = 1
                        else:
                            resp.corr = 0
                        continueRoutine = False
                        FixationLeft.setAutoDraw(False)
                        FixationRight.setAutoDraw(False)
                        keyboard.clearEvents()
                if evt.type == EventConstants.KEYBOARD_RELEASE:
                    if (evt.key == u'left' and Rotation == -2) or (evt.key == u'right' and Rotation == 2):
                        Rotation = 0
            Sample.ori += Rotation
            if Sample.ori > ProbeOri:
                RotDir = 'clockwise'
            elif Sample.ori < ProbeOri:
                RotDir = 'counterclockwise'
            elif Sample.ori == ProbeOri:
                RotDir = 'NA'
            if t >= TestPeriod:
                RT = "NA"
                Sample.setAutoDraw(False)
                if any(Sample.ori > x - MaxError and Sample.ori < x + MaxError for x in OriChecklist):
                    resp.corr = 1
                else:
                    resp.corr = 0
                continueRoutine = False
                FixationLeft.setAutoDraw(False)
                FixationRight.setAutoDraw(False)
                TextBox.text = u'Try to respond faster'
                DispText()                
        if continueRoutine:
            win.flip()
        if event.getKeys(keyList=["escape"]):
            win.close()
            core.quit()
#--------------------

#DATA COLLECTION FUNCTION
#--------------------
def CollectData():
    global ProbeOri, PrimeOri
    while PrimeOri >= 180:
        PrimeOri = PrimeOri - 180
    while PrimeOri < 0:
        PrimeOri = PrimeOri + 180
    CuedOrientation.append(PrimeOri)
    FakeOrientation.append(FPrimeOri)
    CuedOrientationNonJittered.append(CuedOriSchedule[CurrentPos])
    FakeOrientationNonJittered.append(NonCuedOriSchedule[CurrentPos])
    CuedHemisphere.append(CuedHemiSchedule[CurrentPos])
    TrialMarginError.append(min(abs(Sample.ori-x) for x in OriChecklist))
    TrialMarginErrorNonCued.append(min(abs(Sample.ori-x) for x in FOriChecklist))
    AverageMarginError.append(sum(TrialMarginError) / float(len(TrialMarginError)))
    DeviationfromCued.append(DeviationSchedule[CurrentPos])
    while ProbeOri >= 180:
        ProbeOri = ProbeOri - 180
    while ProbeOri < 0:
        ProbeOri = ProbeOri + 180
    ProbeOriList.append(ProbeOri)
    DeviationfromNonCued.append(NonCuedOriSchedule[CurrentPos] - (CuedOriSchedule[CurrentPos] + DeviationSchedule[CurrentPos]))
    TrialReward.append(RewardSchedule[CurrentPos])
    TrialRT.append(RT)
    TrialAcc.append(resp.corr)
    RotList.append(RotDir)
    while Sample.ori >= 180:
        Sample.ori = Sample.ori - 180
    while Sample.ori < 0:
        Sample.ori = Sample.ori + 180
    if RotDir == 'clockwise':
        if Sample.ori < PrimeOri:
            ShootDistList.append((min(abs(Sample.ori-x) for x in OriChecklist)) * (-1))
        elif Sample.ori > PrimeOri:
            ShootDistList.append((min(abs(Sample.ori-x) for x in OriChecklist)))
        else:
            ShootDistList.append(0)
    elif RotDir == 'counterclockwise':
        if Sample.ori < PrimeOri:
            ShootDistList.append((min(abs(Sample.ori-x) for x in OriChecklist)))
        elif Sample.ori > PrimeOri:
            ShootDistList.append((min(abs(Sample.ori-x) for x in OriChecklist)) * (-1))
        else:
            ShootDistList.append(0)
    elif RotDir == 'NA':
        ShootDistList.append(NA)
    FinalOri.append(Sample.ori)
    BlockNumber.append(BlockNum)
    MaxErrorPerm.append(MaxError)
    ParticipantID.append(Participant)
    ConditionList.append(Condition)
    IterationList.append(Iteration)
    Jitter.append(JitterQuant)
    #create dictionary from test data lists and dataframe from this dictionary and .csv file from this dataframe, which will be saved in the local data folder
    data_dict  = {col1: MaxErrorPerm, col2: CuedOrientation, col3: FakeOrientation, col4: CuedHemisphere, col5: AverageMarginError, col6: DeviationfromCued, col7: DeviationfromNonCued, col8: TrialReward, col9: TrialMarginError, col10: TrialRT, col11: TrialAcc, col12: FinalOri, col13: BlockNumber, col14: ParticipantID, col15: ConditionList, col16: TrialMarginErrorNonCued, col17: CuedOrientationNonJittered, col18: Jitter, col19: FakeOrientationNonJittered, col20: IterationList, col21: ProbeOriList, col22: RotList, col23: ShootDistList}
    schedule_dict = {'CuedOriSchedule': CuedOriSchedule, 'NonCuedOriSchedule': NonCuedOriSchedule, 'CuedHemiSchedule': CuedHemiSchedule, 'DeviationSchedule': DeviationSchedule, 'RewardSchedule': RewardSchedule}
    data_frame = pd.DataFrame(dict([(k,Series(v)) for k,v in data_dict.iteritems()]))
    schedule_frame = pd.DataFrame(dict([(k,Series(v)) for k,v in schedule_dict.iteritems()]))
    data_frame.to_csv(os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding()) + '/data/%s_VWMInt_output.csv' % Participant, sep= '\t')
    schedule_frame.to_csv(os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding()) + '/data/%s_VWMInt_currentschedule.csv' % Participant, sep= '\t')
#--------------------

#TUTORIAL DISPLAY FUNCTION
#--------------------
def DispTutorial():
    if Iteration == 0 or Iteration == 2 or Iteration == 3 or Iteration == 4:
        if TutorialPos == 0:
            TextBox.text = u'At the start of every trial, a fixation diamond will appear at the center of the screen. Fixate your gaze on the diamond and do you best not to look elsewhere.'
        elif TutorialPos == 1:
            TextBox.text = u'Soon after, two gratings will appear on screen. Note that they differ in orientation. They will soon disappear, so your job is to hold onto the orientations of these gratings in memory. Remember to stay focused on the fixation diamond.'
        elif TutorialPos == 2:
            TextBox.text = u'After the gratings disappear, two masks will take their place. You will not need to remember anything about the masks. Continue to hold onto the orientations of the gratings and stay focused on the fixation diamond.'
        elif TutorialPos == 3:
            TextBox.text = u'Eventually the fixation diamond will turn bright green on either the left or right side. This is your cue to forget the orientation of the grating that was toward the non-green side of the diamond. Keep the orientation of the grating that was toward the green side of the diamond in memory, and remember to stay focused on the diamond.'
        elif TutorialPos == 4:
            TextBox.text = u'Next, the mask toward the green side of the diamond will be replaced with a new grating. This grating\'s orientation is different than that of the grating that you are to remember. To fix this, please rotate the new grating to match the orientation of the remembered grating as best as you can. Press the RIGHT ARROW key to rotate clockwise and the LEFT ARROW key to rotate counterclockwise. Press the UP ARROW key when you have finished your rotation. Note that you will not have much time to complete your rotation, so act as quickly as you can. If your run out of time however, your trial will still be successful if your rotation is close enough.'
        elif TutorialPos == 5:
            TextBox.text = u'Now that you\'ve reviewed the procedures of the experiment, let\'s try three trials without any interruptions. After each trial, you\'ll be presented with your error in degrees for that trial.'
        elif TutorialPos >= 6:
            TextBox.text = u'Your error was %r\xb0. Press any key to continue.' % min(abs(Sample.ori-x) for x in OriChecklist)
    elif Iteration == 1:
        if TutorialPos == 0:
            TextBox.text = u'At the start of every trial, a fixation diamond will appear at the center of the screen. Fixate your gaze on the diamond and do you best not to look elsewhere.'
        elif TutorialPos == 1:
            TextBox.text = u'Soon after, two gratings will appear on screen. Note that they differ in orientation. They will soon disappear, so your job is to hold onto the orientations of these gratings in memory. Remember to stay focused on the fixation diamond.'
        elif TutorialPos == 2:
            TextBox.text = u'Eventually the fixation diamond will reappear and be colored bright green on either the left or right side. This is your cue to forget the orientation of the grating that was toward the non-green side of the diamond. Keep the orientation of the grating that was toward the green side of the diamond in memory, and remember to stay focused on the diamond.'
        elif TutorialPos == 3:
            TextBox.text = u'Next, the mask toward the green side of the diamond will be replaced with a new grating. This grating\'s orientation is different than that of the grating that you are to remember. To fix this, please rotate the new grating to match the orientation of the remembered grating as best as you can. Press the RIGHT ARROW key to rotate clockwise and the LEFT ARROW key to rotate counterclockwise. Press the UP ARROW key when you have finished your rotation. Note that you will not have much time to complete your rotation, so act as quickly as you can. If your run out of time however, your trial will still be successful if your rotation is close enough.'
        elif TutorialPos == 4:
            TextBox.text = u'Now that you\'ve reviewed the procedures of the experiment, let\'s try three trials without any interruptions. After each trial, you\'ll be presented with your error in degrees for that trial.'
        elif TutorialPos >= 5:
            TextBox.text = u'Your error was %r\xb0. Press any key to continue.' % min(abs(Sample.ori-x) for x in OriChecklist)
    if (Iteration != 1 and TutorialPos < 5) or (Iteration == 1 and TutorialPos < 4):
        TextBox.pos = [0,9]; TextBox.wrapWidth=40; TextBox.alignHoriz='center'; TextBox.height=TutorialSize
    else:
        TextBox.pos = [0,0]; TextBox.wrapWidth=40; TextBox.alignHoriz='center'; TextBox.height=NormalSize
    DispText()
#--------------------







#EXECUTABLE CODE
#////////////////////////////////////////////////

if __name__ == "__main__":
    SetTrainingSchedule()
    main()
    core.quit()