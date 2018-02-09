<?PHP
session_start();
if (!(isset($_SESSION['login']) && $_SESSION['login'] != '')) {
	header ("Location: login3.php");
}
//print ("I recommend a combination of PHP and python scripts<BR>");

?>

<?PHP

$user_name = "root";
//database password here
$pass_word = "";
$database = "security_log";
$server = "127.0.0.1";

$db_handle = mysql_connect($server, $user_name, $pass_word);
$db_found = mysql_select_db($database, $db_handle);

if ($db_found) {

//	print ("in if");
	$SQL = "SELECT * FROM events";

        $result = mysql_query($SQL);

        while ($db_field = mysql_fetch_assoc($result)){

		print "Event: ".$db_field['num']."<BR>";
		print "Sensor: ".$db_field['sensor']."<BR>";
		print "Time: ".$db_field['time']."<BR>";
		$image = $db_field['pic_path'];
		print "<img src=\"$image\" width =\"600\" height=\"400\">";
		print "<br><br>";
	}

	mysql_close($db_handle);

}else{
	print "DB not found";
	mysql_close($db_handle);
}

//print ("in outer php");

?>



	<html>
	<head>
	<title>IOT Device Management Interface</title>


	</head>
	<body>




<P>
<A HREF = page2.php>Log out</A>

	</body>
	</html>
