<?PHP


//==========================================
//	ESCAPE DANGEROUS SQL CHARACTERS
//==========================================
function quote_smart($value, $handle) {

   if (get_magic_quotes_gpc()) {
       $value = stripslashes($value);
   }

   if (!is_numeric($value)) {
       $value = "'" . mysql_real_escape_string($value, $handle) . "'";
   }
   return $value;
}

if ($_SERVER['REQUEST_METHOD'] == 'POST'){
	$uname = $_POST['username'];
	$pword = $_POST['password'];

	$uname = htmlspecialchars($uname);
	$pword = htmlspecialchars($pword);

	//==========================================
	//	CONNECT TO THE LOCAL DATABASE
	//==========================================
	$user_name = "root";
        //database password here
	$pass_word = "";
	$database = "iotdevdb";
	$server = "127.0.0.1";

        $db_handle = mysql_connect($server, $user_name, $pass_word);
        $db_found = mysql_select_db($database, $db_handle);

//        print "DB Read Ooperation";
        if ($db_found) {
//            echo "$uname:$pword:";
            $epw = md5($pword);

            $uname = quote_smart($uname, $db_handle);
            $pword = quote_smart($pword, $db_handle);

//            echo ":$uname:$pword:";

            $SQL = "SELECT * FROM login WHERE (L1 = $uname AND L2 = '$epw')";
//            $SQL = "SELECT * FROM login WHERE L2 = '$epw'";
//            $SQL = "SELECT * FROM login WHERE L1 = $uname";
//            echo "$SQL";
            $result = mysql_query($SQL);
            $num_rows = mysql_num_rows($result);



	//====================================================
	//	CHECK TO SEE IF THE $result VARIABLE IS TRUE
	//====================================================
//echo "- $num_rows -";
		if ($num_rows) {
	 	   session_start();
		   $_SESSION['login'] = "1";
		   header ("Location: page1.php");
		}
		else {
			$errorMessage = "Error logging on";
		}

	mysql_close($db_handle);

    }
}
?>


<html>
<head>
<title>Basic Login Script</title>
</head>
<body>

<FORM NAME ="form1" METHOD ="POST" ACTION ="login3.php">

Username: <INPUT TYPE = 'TEXT' Name ='username'  value="<?PHP print $uname;?>" maxlength="20">
Password: <INPUT TYPE = 'TEXT' Name ='password'  value="<?PHP print $pword;?>" maxlength="16">

<P>
<INPUT TYPE = "Submit" Name = "Submit1"  VALUE = "Login">


</FORM>

<P>
<?PHP print $errorMessage;?>




</body>
</html>
