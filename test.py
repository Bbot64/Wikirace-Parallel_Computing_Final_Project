import wikipediaapi
import os
import multiprocessing
import time

wiki_wiki = wikipediaapi.Wikipedia('en')       # Sets the Wikipedia language.

def serialOrParallel():
    # This function allows the user to enter whether they want to run the code in parallel or not.
    while (True):
        parallel = input("\nWould you like to test the code in parallel? 1: Yes. 0: No. ")
        if parallel == str(1):
            return True
        elif parallel == str(0):
            return False
        else:
            print("Invalid input entered.")

def validateTime():
    # This funcion is responsible for letting the user enter the maximum amount of time for the search.
    validTime = False
    while (not(validTime)):
        maxTime = input("Please enter the maximum amount of time to search for the end page in seconds as an integer (60 second minimum - 600 second maximum): ")
        try:
            val = int(maxTime)
            if val >= 60 and val <= 600:
                maxTime = val
                validTime = True
            else:
                print("Invalid time entered.")
        except ValueError:
            print("Time must be a number.")
    return maxTime

def isDuplicate(currPage, pages):
    # This function checks whether a user entered start page is the same as another start page already entered.
    # It compares the name of every page in the pages list to the current page.
    # If they are the same, then it returns True. Otherwise, it returns False.
    for page in pages:
        if (page.title == currPage.title):
            return True
    return False

def validateCPUCount():
    # This function ensures a valid number corresponding to the maximum number of processors is returned. 
    count = os.cpu_count()
    if (count is None):
        # This will only be entered if os.cpu_count() does not return a valid number
        validCPU = False
        while(not(validCPU)):
            count = input("Please enter the maximum number of processes you'd like to use: ")
            try:
                val = int(count)
                if val > 0:
                    count = val
                    validCPU = True
                else:
                    print("Please enter a number greater than zero.")
            except ValueError:
                print("Please enter a number.")
    return count

def enterWikiPages():
    cpu_count = validateCPUCount()
    # This function is in charge of the user entering wikipedia pages. We decided the max amount of pages a user could enter is equal
    # to the number of cores the user has. The user also could stop at any time entering pages. 
    print("Please enter up to", cpu_count, "valid Wikipedia pages to begin searching from. Capitalization matters!")
    startPages = []
    count = 0
    while(count < os.cpu_count()):
        startPage = validateWikiPage()
        if (isDuplicate(startPage, startPages)):
            print("Duplicate page entered. Please enter a non-duplicate page.")
            continue
        startPages.append(startPage)
        count += 1
        print(count, "Pages(s) entered out of", os.cpu_count(), "pages.")
        if (count == os.cpu_count()):
            break
        else:
            while (True):
                # This part of the function allows the user to continue or stop entering pages.
                # The user will not get to this point if he/she has already entered the max amount of pages.
                complete = input("Continue entering start pages? 1: Yes. 0: No.\n")
                if complete == str(0):
                    finished = True
                    break
                elif complete == str(1):
                    finished = False
                    break
                else:
                    print("Invalid input entered.")
        if finished:
            break
    return startPages

def validateWikiPage(msg="Please enter a valid wikipedia page. "):
    # This function validates that the user entered a valid page.
    # E.g. if the enters gibberish that doesn't correspond to a Wikipedia page,
    # then the user must reenter a page.
    while(True):
        page = input(msg)
        wiki_page = wiki_wiki.page(str(page))
        if (not(wiki_page.exists())):
            print("Wikipedia page does not exist. ")
        else:
            break
    return wiki_page

def removeAlreadyVisitedPages(list1: list, list2: list):
    # This function removes items from list1 that exist within list2.
    newList = [i for i in list1 if i not in list2]
    return newList

def pageSearch(sp, ep, mt):
    # This function is responsible for the main search loop of the function
    begin = time.time()         # The start time is recorded
    currPage = sp               # The current page is set as the start page
    links = []                  # An empty list of links is created
    pages = [currPage.title]    # A pages list is initialized with only the current page's title in it
    totalPageVists = 1          # Only the current page (the start page) has been "visited," so this count is initially 1.
    finished = False            # Nothing has been found or finished, so both are set to False
    found = False  
    while(not(finished)):       # The while loop continues until finished is True
        if (currPage.title == ep):      # If the current page is the end page, then the end page has been found and the loop is broken.
            finished, found = True, True
            break
        else:                           # Else, every link on the current page is gone through.
            for link in currPage.links.keys():
                if (link == ep):                        # If one of these links is the end page, then the end page has been found and the loop is broken.
                    currPage = wiki_wiki.page(link)     # The current page is set to the start page, the title is appended to the list of pages, count increments by 1
                    pages.append(currPage.title)        # And the boolean vars are updated.
                    totalPageVists += 1
                    finished, found = True, True
                    break
                else:
                    links.append(link)                  # Else, the link is appended to a list of links
            if (finished):
                break                                   # If the end page had been found in the links above, it would enter here and break the loop
            links = list(dict.fromkeys(removeAlreadyVisitedPages(links, pages)))        # Already visited pages are removed from the links, as well as duplicate link entries.
            while(True):
                if (len(links) > 0):                    # If there are entries in the links list...
                    currPage = wiki_wiki.page(links[0])     # The current page is set as the first link in the list.
                    pages.append(currPage.title)            # The page is appended to the page list.
                    links.pop(0)                            # This link is then removed from the list.
                    if (currPage.exists()):                 # This section ensures the current link exists (sometimes a page link doesn't point anywhere).
                        totalPageVists += 1                 # If it does, then the count increments and this while loop is broken.
                        break
                else:                                   # If there are no links to visit, then the search is finished and the result has not been found.
                    finished = True
                    found = False
                    break
            if (time.time() - begin > mt):      # If the time to find the solution has exceeded the max time, then the search finishes without a solution.
                finished = True
                found = False
    if (found):
        end = time.time()
        print("Total time to find", ep, "from", sp.title, ":", end - begin, "seconds.")
    else:
        print(ep, "could not be found from", sp.title, "within the max time of", mt, "seconds.")
    print("Total page visits: ", totalPageVists)
        
def main():
    print("EXAMPLE start pages to begin a search from include 'Python', 'Monty Python', 'Jimmy Kimmel', 'OK', etc. ")
    startPages = enterWikiPages()       # The user enters all the Wikipedia pages to begin searching from.

    print("\nAn EXAMPLE end page to search for is 'Primetime Emmy Award'")
    endWikiPage = validateWikiPage("Please enter the wikipedia page to SEARCH FOR: ")   # The user enters the Wikipedia page to search for.

    print("\nEXAMPLE: It took nearly ~100 seconds to locate 'Primetime Emmy Award' from 'Python'")
    maxTime = validateTime()    # The user enters the maximum amount of time to find the solutions.
    parallel = serialOrParallel()   # The user can decide whether to run the code in parallel or not.

    if (parallel):
        processes = []      # This list will contain all the processes
        for i in range(len(startPages)):    # The length of the list will affect how many processes are created: A process for each start Wikipedia page.
            p = multiprocessing.Process(target=pageSearch, args=[startPages[i], endWikiPage.title , maxTime])
            p.start()
            processes.append(p)
        for process in processes:
            process.join()
    else:
        for startPage in startPages:
            pageSearch(startPage, endWikiPage.title, maxTime)
     
    x = input("Press Enter to exit: ")

if __name__ == "__main__":
    main()