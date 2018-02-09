<html>
<head>
<title>Web Server Template Application</title>
</head>
<body bgcolor=white>

<?PHP

echo "Start of page to validate";

session_start();
if (!(isset($_SESSION['login']) && $_SESSION['login'] != '')) {
        header ("Location: login3.php");
}

echo "back to validated window";
?>

<h1>Sample IOT Web Server Template</h1>
<p>This is the home page for a sample application used to illustrate the


</body>
</html>
