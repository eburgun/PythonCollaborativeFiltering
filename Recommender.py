

import CSR
import time
import math

class Recommender:

    def __init__(self,trainingFile,testFile,kVal,nVal,outFile):
        start = time.clock()
        self.__nValue = nVal
        self.__kValue = kVal
        self.__outFile = outFile
        self.__trainingData = CSR.CSR(trainingFile)
        self.__trainingTranspose = CSR.CSR(trainingFile)
        self.__trainingTranspose.transpose()
        self.__testData = CSR.CSR(testFile)
        self.__cosDict = {}
        self.__nkBuilt = False
        self.__kChanged = False
        
        setupTime = time.clock() - start
        print setupTime
        
    def recommendations(self):
        cumulativeTime = 0
        self.__userRecs = []
        if not self.__nkBuilt:
            self.__buildNKArray()
        if self.__kChanged:
            self.__rebuildNK()
            
        for i in xrange(self.__trainingData.rows):
            start = time.clock()
            self.__userRecs.append(self.__pullKTopVals(i))
            end = time.clock()
            cumulativeTime += end - start
        print cumulativeTime
    
    def __buildNKArray(self):
        start = time.clock()
        self.__lengthArray = [0] * self.__trainingTranspose.rows
        cosArray = [0] * self.__trainingTranspose.rows
        self.__nkArray = [[[0.0,0]for j in xrange(2 * self.__kValue)]for i in xrange(self.__trainingTranspose.rows)]
        
        for i in xrange(len(self.__lengthArray)):
            itemStart = self.__trainingTranspose.row_ptr[i]
            itemFinish = self.__trainingTranspose.row_ptr[i+1]
            
            while itemStart < itemFinish:
                self.__lengthArray[i] += self.__trainingTranspose.rating[itemStart] * self.__trainingTranspose.rating[itemStart]
                itemStart += 1

            
        for i in xrange(self.__trainingTranspose.rows):
            itemStart = self.__trainingTranspose.row_ptr[i]
            itemFinish = self.__trainingTranspose.row_ptr[i+1]
            while itemStart < itemFinish:
                colStart = self.__trainingData.row_ptr[self.__trainingTranspose.column_idx[itemStart]]
                colFinish = self.__trainingData.row_ptr[self.__trainingTranspose.column_idx[itemStart]+1]
                while colStart < colFinish:
                    if self.__trainingData.column_idx[colStart] != i:
                        cosArray[self.__trainingData.column_idx[colStart]] += self.__trainingData.rating[colStart] * self.__trainingTranspose.rating[itemStart]
                    colStart += 1
                itemStart += 1
            for j in xrange(len(cosArray)):
                if self.__lengthArray[i] != 0 and self.__lengthArray[j] != 0:
                    cosArray[j] /= math.sqrt(self.__lengthArray[i]) * math.sqrt(self.__lengthArray[j])
                    
                    if i < j:
                        if not self.__cosDict.has_key(str(i) + " " + str(j)) and not self.__cosDict.has_key(str(j) + " " + str(i)):
                            self.__cosDict[str(i) + " " + str(j)] = cosArray[j]
                    elif j < i:
                        if not self.__cosDict.has_key(str(i) + " " + str(j)) and not self.__cosDict.has_key(str(j) + " " + str(i)):
                            self.__cosDict[str(j) + " " + str(i)] = cosArray[j]
                else:
                    cosArray[j] = 0
                if cosArray[j] > self.__nkArray[i][len(self.__nkArray[i])-1][0]:
                    self.__nkArray[i][len(self.__nkArray[i])-1][0] = cosArray[j]
                    self.__nkArray[i][len(self.__nkArray[i])-1][1] = j
                    
                    k = len(self.__nkArray[i]) - 1
                    while self.__nkArray[i][k][0] > self.__nkArray[i][k-1][0] and k > 0:
                        temp = self.__nkArray[i][k-1]
                        self.__nkArray[i][k-1] = self.__nkArray[i][k]
                        self.__nkArray[i][k] = temp
                        k -= 1
            for j in xrange(len(cosArray)):
                cosArray[j] = 0
        self.__kChanged = False
        self.__nkBuilt = True
        print ""
        print "Build Time"
        print time.clock() - start
        
        
    def __rebuildNK(self):
        start = time.clock()
        self.__nkArray = [[[0.0,0]for j in xrange(2*self.__kValue)]for i in xrange(self.__trainingTranspose.rows)]
        
        for i in xrange(self.__trainingTranspose.rows):
            for j in xrange(self.__trainingTranspose.rows):
                curSimil = 0
                if self.__lengthArray[i] != 0 and self.__lengthArray[j] != 0:
                    if i < j:
                        curSimil = self.__cosDict[str(i) + " " + str(j)]
                    elif j < i:
                        curSimil = self.__cosDict[str(j) + " " + str(i)]
                if curSimil > self.__nkArray[i][len(self.__nkArray[i])-1][0]:
                    self.__nkArray[i][len(self.__nkArray[i])-1][0] = curSimil
                    self.__nkArray[i][len(self.__nkArray[i])-1][1] = j
                    
                    k = len(self.__nkArray[i]) - 1
                    while self.__nkArray[i][k][0] > self.__nkArray[i][k-1][0] and k > 0:
                        temp = self.__nkArray[i][k-1]
                        self.__nkArray[i][k-1] = self.__nkArray[i][k]
                        self.__nkArray[i][k] = temp
                        k -= 1
            
        self.__kChanged = False
        print ""
        print "Build Time"
        print time.clock() - start
        
    def __testRecsHR(self):
        hits = 0.0
        aRHR = 0.0
        for i in xrange(self.__testData.rows):
            inRec = False
            jVal = 0
            for j in xrange(len(self.__userRecs[i])):
                if self.__testData.column_idx[i] == self.__userRecs[i][j][1]:
                    inRec = True
                    jVal = j + 1
            if inRec == True:
                hits += 1.0
            if jVal != 0:
                aRHR += 1.0/jVal
                
        hitRate = hits / self.__testData.rows
        aRHR /= self.__testData.rows
        return hitRate,aRHR
    
    def saveRecs(self):
        saveFile = open(self.__outFile,'w')
        for i in xrange(self.__trainingData.rows):
            userString = str(i + 1) + ":"
            for j in xrange(len(self.__userRecs[i])):
                userString += " " + str(self.__userRecs[i][j][1] + 1)
                userString += " " + str(self.__userRecs[i][j][0]) 
            saveFile.write(userString + "\n")
        
        saveFile.close()
        
    def changeNValue(self,newN):
        self.__nValue = newN

    def changeKValue(self,newK):
        self.__kValue = newK
        self.__kChanged = True
        
    def changeOutFile(self,newFileName):
        self.__outFile = newFileName
        
    def __pullKTopVals(self,userID):
        userItemCount = self.__trainingData.row_ptr[userID + 1] - self.__trainingData.row_ptr[userID]
        userItems = [0] * userItemCount
        
        for i in xrange(len(userItems)):
            userItems[i] = self.__trainingData.column_idx[self.__trainingData.row_ptr[userID] + i]
        kList = []
        inList = []
        for i in xrange(userItemCount):
            j = 0
            itemCount = 0
            while j < len(self.__nkArray[i]) and itemCount < self.__kValue:
                if self.__nkArray[i][j][1] not in userItems and self.__nkArray[i][j][1] not in inList:
                    inList.append(self.__nkArray[i][j][1])
                    kList.append([0,self.__nkArray[i][j][1],[j]])  
                    itemCount += 1
                
                j += 1
       
        self.rankKVals(userItems,kList)
        self.__quickSort(kList)
        nValues = []
        for i in xrange(self.__nValue):
            nValues.append(kList[i])
        return nValues
    
    def rankKVals(self,itemsArray,kList):
        for i in xrange(len(kList)):
            for j in xrange(len(itemsArray)):
                if kList[i][1] < itemsArray[j]:
                    kList[i][0] += self.__cosDict[str(kList[i][1]) + " " + str(itemsArray[j])]
                    kList[i][2].append(itemsArray[j])
                elif itemsArray[j] < kList[i][1]:
                    kList[i][0] += self.__cosDict[str(itemsArray[j]) + " " + str(kList[i][1])]
                    kList[i][2].append(itemsArray[j])
    
    """
    A method for determining hit rate and average reciprical hit rate for various k and n values 
    """
    def testingMethod(self):
        start = time.clock()
        testFile = open('results.txt','w')
        kVals = [3,5,10,20]
        nVals = [5,10,20]
        for i in xrange(len(kVals)):
            self.changeKValue(kVals[i])
            for j in xrange(len(nVals)):
                self.changeNValue(nVals[j])
                self.recommendations()
                HR,ARHR = self.__testRecsHR()
                testFile.write(str(kVals[i]) + " " + str(nVals[j]) + " " + str(HR) + " " + str(ARHR) + "\n")
        testFile.close()
        print time.clock() - start
        
    def __insertionSort(self,array,left,right):
        
        for i in range(right - left + 1):
            
            temp = array[i + left]
            j = i + left
            while(j > left and temp[0] > array[j-1][0]):
                array[j] = array[j-1]
                j -= 1
            array[j] = temp
    """
    This method just swaps two objects within the array being sorted.
    """
    def __swap(self,array,a,b):
        
        temp = array[a]
        array[a] = array[b]
        array[b] = temp
    """
    This method determines the pivot value based on the provided subsection limits. Then it moves the pivot value to just next to the farthest left position.
    """
    def __pivot(self,array,left,right):
        center = (left + right) / 2
        
        if array[center][0] < array[right][0]:
            self.__swap(array,right,center)
        if array[left][0] < array[right][0]:
            self.__swap(array,right,left)
        if array[left][0] < array[center][0]:
            self.__swap(array,center,left)
        
        self.__swap(array,center,(left + 1))
        return array[left + 1][0]
    """
    This is the major function within the quick sort process. The input is the array it is to sort, 
    the first position of the subsection it is working on, and the last position of the subsection it
    is working on. It starts by checking the size of the subsection. If the subsection is less than 
    or equal to 5 items it will run an insertion sort on the subsection. Otherwise it continues to 
    quick sort.
    """
    def __partition(self,array,left,right):
        
        if (right - left) > 5:
            pivotValue = self.__pivot(array,left,right)
            
            i = left + 1
            j = right
            
            while i < j:
                i += 1
                while pivotValue < array[i][0]:
                    i += 1
                while array[j][0] < pivotValue:                    
                    j -= 1
                
                if i < j:
                    
                    self.__swap(array,i,j)
            
            self.__swap(array,j,(left + 1))
            
            self.__partition(array,left,j-1)
            self.__partition(array,j+1,right)
        
        else:
            self.__insertionSort(array,left,right)
    """
    This method just starts the quick sort process with a provided array.
    """
    def __quickSort(self, array):
        self.__partition(array,0,len(array) - 1)