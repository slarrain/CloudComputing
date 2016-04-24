<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  </head>

  <body>
    <h1>AnnTools Job Request</h1>

    <form id="upload_form" action="https://{{bucket_name}}.s3.amazonaws.com/" method="post" enctype="multipart/form-data">
      <!-- Include required AWS S3 parameters as hidden fields here -->
    <!-- Minimum required: S3 key, acl, policy, signature, AWS Access Key -->
      <!-- As an example, the AWS Access Key is shown below -->
      <input type="hidden" name="AWSAccessKeyId" value="{{aws_key}}">
      <input type="hidden" name="key" value="{{aws_username}}/{{filename_id}}-${filename}">
      <input type="hidden" name="acl" value="public-read">
      <input type="hidden" name="success_action_redirect" value="http://54.174.243.246/annotator">
      <input type="hidden" name="policy" value={{policy_encod}}>
      <input type="hidden" name="signature" value={{signat}}>

      Select input file: <input id="upload_file" type="file" name="file" />

      <input type="submit" value="Upload Input File" />
    </form>
  </body>
</html>
