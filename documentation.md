The App Functionality is fairly simple. Focus on adding the core functionality, so that you have something you can actually submit, then if time permits add any thing extra. 

### Child Side:

##### Login/Logout
This is the simplest one, from UI prespective, we only need two functionalities: 1) Sign in 2) Sign out.
The sign in functionality is extended, if this device is being setup for the first time or reinstall. In this case, walk the parent through a simple steps, to show him how he can access device settings, to give application system control, to be able to deny child from deleting the app unless the application is explicitly logged in. Then, that's it!

##### Application Blocking
Need to find a way, that if the child tires to access a specific application that the parent chose to be blocked "lets say, Instagram", then the child should receive the same message that he cannot access the application, and the details should be sent to backend from child device, so that the backend can save the data in the database

***solution***
*Either*
- Detect when blocked app comes to foreground
- Immediately overlay your block screen activity with `FLAG_ACTIVITY_NEW_TASK`
- **Key permission:** `PACKAGE_USAGE_STATS`
create a background service polling `UsageStatsManager.queryEvents()` every few seconds.

*Or*
**AccessibilityService with `TYPE_WINDOW_STATE_CHANGED` event** - get notified when apps launch instead of polling.
AccessibilityService listens to WINDOW_STATE_CHANGED event
→ Get callback when window changes (app launches)
→ Check package name
→ Block if needed
##### Deny deletion of application 
The app cannot be deleted unless the parent log in with correct account credentials. 
**Core mechanism:** Android's **Device Administration API** (DeviceAdminReceiver)

**How it works:**

1. App requests Device Admin privileges during setup
2. Once activated, Android blocks uninstallation unless admin is deactivated
3. Your app requires parental credentials to deactivate admin privileges


**Key APIs:**

- `DevicePolicyManager`
- `DeviceAdminReceiver` (extend this class)

**Search terms:**

- "Android DeviceAdminReceiver prevent uninstall"
- "DevicePolicyManager parental control example"

```
Child taps uninstall
↓
Android: "Cannot uninstall - device admin active"
↓  
Child must open app → Settings → Disable Protection
↓
App prompts: password → verification code → biometric
↓
All pass → DevicePolicyManager.removeActiveAdmin()
↓
Now uninstallable
```

### Parent side:
##### Blocking Section
This will be either a simple web app, or a chrome extension, but most likely a web app since I believe it'll be simpler and more straightforward. 
The parent will have access to core functionalities, like blocking specific applications, or blocking specific websites that he don't want his child to access. Either, it'll be an explicit link, or it can be a general category like adult content so that any website tagged or featured with this tag will be blocked on the child's device.
This is the blocking section. 

##### Report Section
This will be simpler than blocking section, it'll simply be the web app retriving the reports from the server database, and displaying it to the parent. With all the details mentioned about the Report, like screenshot, time, etc...

### Backend side:
##### Website Blocking
This is where the heavy lifting will be. But not that heavy, I believe. Need to find a free way, to be able to have the black list. There's tons of lists on the internet, so we could use that, or we could use a firewall of some sort, or, VPN. This is for website search, and blocking certain categories like Gambling, Porn, or any other type we want.

***solution***: 
**Category blocking:** Use **public DNS blocklists** (Steven Black's hosts, OISD blocklist)

**Specific URL blocking:** Maintain your own SQLite database of blocked domains:
	- Simpler than categories - just string matching against domains



##### Report Formatting
This is the simplest feature, in which the backend simply retrieves the latest report data from the database, formats it in a nice way to present it to the parent, then forwards this report to the parent's front-end side, where now the front end will display that data for the parent.


# Requirements:
## Child Client
1) Login
2) Log out
3) Deny app deletion
4) Deny access to blacklisted applications

> Android Development: Java/Kotlin
## Parent Client
1) Block Websites
	- By Category
	- By Specific website link

2) Block Applications
3) Review Reports

> React Library
## Server Backend 
1) Website Blocking implementation
2) Format Report in Readable way after retreiving data from database
3) Send blocked lists/categories and applications to child client 
4) Persist data sent about child activity from child client to database
5) Persist blocking lists chosen by parent in parent client to database

> Programming Language: Python or Nodejs or Java.
> Database: Postegres or MySql or Sqlite 


![[Software Architecture -2.jpg]]