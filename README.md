These are python scripts that help automate the configuring of NPA private applications in a Netskope tenant.

  tron-read-app will read the private apps from the tenant, read the publisher name and put them into an excel file.
  
  tron-get-publishers will read the publishers and get the name, theCN, the ID, adn IP address.   The name and ID are required to create a new private app.

  tron-create-apps will take read an excel file and create private apps based on its contents.
  
  The excel file sample-excel.xlsx is a sample file use for tron-create-apps.


