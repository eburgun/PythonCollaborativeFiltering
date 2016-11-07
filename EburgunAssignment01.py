# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 16:25:15 2016

@author: eburgun

Due september 28th!
"""

import sys
import Recommender
    
running = True
trainingFile = sys.argv[1]
testFile = sys.argv[2]


kValue = 3
nValue = 5
outFile = "Output.txt"


print "Hello, welcome to this Recommender System!"
print "Please wait while we load your data."

recommend = Recommender.Recommender(trainingFile,testFile,kValue,nValue,outFile)

print "Data loaded."
print "Please choose from the options below:"
print "1. Define K Value. (Default == 3)"
print "2. Define N Value. (Default == 5)"
print "3. Define Output File. (Default == Output.txt)"
print "4. Run Recommendation system."
print "5. Save User Recommendations."
print "6. Create Test Report"
print "Q. Exit"

recHasRun = False
testHasRun = False
while running:
    
    userInp = raw_input("What is your choice? ")
    
    if userInp == "1":
        while userInp == "1":
            KInput = raw_input("Please input desired K value. ")
            if KInput.isdigit() and KInput > 0:
                kValue = KInput
                recHasRun = False
                recommend.changeKValue(int(kValue))
                userInp = 0
            else:
                print "That is not a valid number. Please try again"
            
    elif userInp == "2":
        while userInp == "2":
            NInput = raw_input("Please input desired N value. ")
            if NInput.isdigit() and NInput > 0:
                nValue = NInput
                recHasRun = False
                recommend.changeNValue(int(nValue))
                userInp = 0
            else:
                print "That is not a valid number. Please try again"
                
    elif userInp == "3":
        while userInp =="3":
            FInput = raw_input("Please input desired file name. (Don't forget to include the extension) ")
            recommend.changeOutFile(FInput)
            print FInput
            userInp = 0
            
    elif userInp == "4":
        print "Please wait while we determine user's recommendations."
        recommend.recommendations()
        print "User Recommendations Complete!"        
        recHasRun = True
        userInp = 0
        
    elif userInp == "5":
        if recHasRun == True:
            recommend.saveRecs()
            recommend.changeKValue(3)
            recommend.changeNValue(5)
            userInp = 0
            
        else:
            print "Recommendations have not been determined"
            userInp = 0
        
    elif userInp == "6":
        
        recommend.testingMethod()
        recommend.changeKValue(3)
        recommend.changeNValue(5)
        userInp = 0
        
        
    elif userInp == "Q" or userInp == "q":
        running = False
        
    else:
        print "I'm sorry, I didn't quite catch that"
