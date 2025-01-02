Yum share
| Users |
| 1.Authentication Screen |
  |  Register |
	→ Input: Name, Email, Phone, Password
	→ Encrypt password using bcrypt
	→ Save to database
   | Login  |
	→ Input: Email, Password
	→ Authenticate against the database
	→ Redirect to Home Page if successful
| 2.Home Page |
      | View Recently Uploaded Recipes |
      | Search Recipes by
  	→ Ingredients
	→ Serving Size
	→ Cooking Time |
     | Sort Recipes by
	→ Highest Number of Likes |
    |  Interact with Recipes
	→ Post Comments
	→ Update/Delete Comments
	→ View Comments
     Download Recipe PDFs
     Recipe Upload Screen  |
|3.Input Recipe Details:
	→ Title
	→ Serving Size
	→ Cooking Time
	→ Image
	→ Ingredients
	→ Steps
        Save Recipe |
| 4.Favourites Screen
	View Favourite Recipes
	Remove from Favourites
	Download PDF of Favourite Recipes |
| 5.Your Recipes Screen
	View Uploaded Recipes with Like Counts  |
	Delete Recipes
| 6.Profile Screen
	Update Profile:
	→ Name
	→ Email
	→ Phone
	→ Password
	Update Additional Info:
	→ Bio
	→ Hobby
	→ Profile Photo  |
    
Admin
| Authentication Screen  |->  | Admin Login |
| Admin dashboard       | -> Visualizations
                             ->Bar graph
                             ->Pie chart
                             ->Histogram
                             ->Line graph
                        -> Admin can view no of app users
                               ->HTML file(user_id,username,email,recipe_uploaded_Count,favourites_count)
                               ->CSV file(user_id,username,email,recipe_uploaded_Count,favourites_count)
                               ->PDF file(user_id,username,email,recipe_uploaded_Count,favourites_count)
                        
 














