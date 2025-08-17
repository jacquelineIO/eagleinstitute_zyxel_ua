const express = require('express');
const path = require('path');
const fs = require('fs');
const json2csv = require('json2csv').parse;
const app = express();
const port = 3000;
const cors = require('cors');

// Enable CORS for all origins
app.use(cors());

app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader(
    "Access-Control-Allow-Methods",
    "OPTIONS, GET, POST, PUT, PATCH, DELETE" // what matters here is that OPTIONS is present
  );
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
  next();
});

app.use(express.urlencoded({ extended: true }));
app.use(express.json())


app.post('/append', (req, res) => {
	debugger;
	const email = req.body.field1;
	const date = new Date().toLocaleDateString();
	const time = new Date().toLocaleTimeString();
	const filePath = path.join('//192.168.50.19/exports$', 'export.csv');
	let count = 1;
	let data;
	let csvRows;
	let header;

	if (fs.existsSync(filePath)) {
		var array = fs.readFileSync(filePath).toString().split('\n');
		for(i in array) {
			if (array[i].includes(email))
			{
				count = count + 1;
			}}
			
		header = false;
		}
	else {
		header = true;
	}
	
	data = [{'Email Address': email, 'Date': date, 'Timestamp': time, 'Number of Visits': count}];
		csvRows = json2csv(data, {header: header});
		fs.appendFile(filePath, csvRows.replace(/"/g, '') + '\r\n', (err) => {
			if (err) {
            console.error(err);
            res.status(500).send('Error appending data');
        } else {
            res.send('Data appended successfully');
			console.log('Data appended successfully');
        }
			});	
});


app.listen(port, () => {console.log(`Server listening on port ${port}`);});