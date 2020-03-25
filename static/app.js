var currentTheme = "light";
function themeSetter() {
  var today = new Date();
  var h = today.getHours();
  if (h > 20 || h < 7) {
    $("html").css("background-color", "#212121")
    $("body").css("background-color", "#212121")

    $("#logotip").attr("src", "./static/images/icon-test-dark-alt.png");

    $("#dataTable").addClass("my-table-dark");
    $(".fakeThead").css("background-color", "#212121");
    
    $("thead th").css("background-color", "#212121")
    $("thead th").css("color", "white")

    $(".modal-content").addClass("elegant-color");
    $(".modal-body").addClass("text-white");

    currentTheme = "dark"
    
  }
}

var country = "";
$.getJSON('https://json.geoiplookup.io', function (data) {})
  .done(function (data) {
    country = data.country_name
    colorCountry(country);
  })

var region = "";

// Search
$("#search").on("keyup", function () {
  var value = $(this).val().toLowerCase();
  $("#dataTable tbody tr").filter(function () {
    $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
  });
  colorCountry();
});

function tableBodyCreate(region) {
  var tbl = document.getElementById('dataTable');
  var tbdy = document.createElement('tbody');
  $("#dataTable tbody").empty();
  for (var i = 0; i < data.length; i++) {
    if (data[i]["region"] == region || region == "") {
      var row = tbdy.insertRow();
      var cell = row.insertCell();
      row.setAttribute("class", "countryExpand");
      row.setAttribute("id", i);
      cell.innerHTML = data[i]["slovenianName"]
      cell.setAttribute("id", data[i]["name"])
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      cell.setAttribute("class", "d-none d-lg-table-cell text-right");
      cell.innerHTML = data[i]["countryPopulation"];
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      cell.innerHTML = data[i]["infected"];
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      cell.innerHTML = data[i]["infectedToday"];
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      cell.setAttribute("class", "d-none d-sm-table-cell text-right");
      cell.innerHTML = data[i]["infectedRatio"] + "%";
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      cell.innerHTML = data[i]["dead"];
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      cell.setAttribute("class", "d-none d-sm-table-cell text-right");
      cell.innerHTML = data[i]["deadToday"];
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      cell.setAttribute("class", "d-none d-md-table-cell text-right");
      cell.innerHTML = data[i]["deadRatio"] + "%";
      cell = row.insertCell();
      cell.setAttribute("align", "right");
      cell.setAttribute("class", "d-none d-md-table-cell text-right");
      cell.innerHTML = data[i]["cured"];
    }
  }
  tbl.appendChild(tbdy);
  colorCountry();
}

function tableCreate(region) {
  var headers = ["Država", "Populacija", "Okuženi", "Okuženi danes", "Obolevnost", "Umrli", "Umrli danes", "Umrljivost",
    "Ozdraveli"
  ];
  var headersIcons = ["fas fa-flag", "", "fas fa-biohazard", "fas fa-calendar-day", "", "fas fa-book-dead", "", "",
    "fas fa-smile"
  ];
  var tbl = document.getElementById('dataTable');
  var tbdy = document.createElement('tbody');
  var thdr = tbl.createTHead();
  thdr.setAttribute("id", "tableHead")
  var row = thdr.insertRow();
  for (var i = 0; i < headers.length; i++) {
    var cell = document.createElement("th");
    cell.innerHTML = '<div class="d-none d-sm-block">' + headers[i] + '</div><div class="d-sm-none"><i class="' +
      headersIcons[i] + '"></i></div>'
    if (headers[i] == "Okuženi") {
      cell.setAttribute("data-sort-default", "")
    }
    if (i != 0) {
      cell.setAttribute("class", "text-right col");
    } else {
      cell.setAttribute("class", "col");
      cell.innerHTML = '<div>' + headers[i] + '</div>';
    }
    if (headers[i] == "Ozdraveli" || headers[i] == "Umrljivost") {
      cell.setAttribute("class", "d-none d-md-table-cell text-right col");
    }
    if (headers[i] == "Obolevnost" || headers[i] == "Umrli danes") {
      cell.setAttribute("class", "d-none d-sm-table-cell text-right col");
    }
    if (headers[i] == "Populacija") {
      cell.setAttribute("class", "d-none d-lg-table-cell text-right col");
    }
    row.appendChild(cell);
  }
  tableBodyCreate(region);
}

if (goodResponse == "True") {
  tableCreate(region);
} else {
  var mainDiv = document.getElementById("mainDiv");
  mainDiv.innerHTML =
    '<div class="text-center" style="margin-top: 50px !important;"><h1>Dostop do podatkov trenutno ni mogoč! 😟</h1><p class="lead">Uporabite alternativne spletne aplikacije za pregled podatkov.<br>👉 <a href="https://www.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6">COVID-19 Tracker by CSSE</a></p></div>';
  var footerDiv = document.getElementById("footerDiv")
}
  // Zaženemo plugin za sortiranje
new Tablesort(document.getElementById("dataTable"), {
  descending: true
});
themeSetter();
colorCountry();

function colorCountry() {
  var table = $("#dataTable");
  var rows = table.find("tr");
  for (var i = 1; i < rows.length; i++) {
    var cells = rows[i].getElementsByTagName("td")
    if (cells[0].getAttribute("id")==country) {
      rows[i].classList.add("myCountry");
      rows[i].style.backgroundColor = "#ffff72";
      rows[i].style.color = "black";
    }
  }
};

$(document).on(colorCountry(), "#dataTable", function(){});

$(document).ready(function() {
  $(document).on("click", ".countryExpand" , function() {
    var i = $(this).attr("id");
    $("#countryDetailsModalTitle").text(data[i]["slovenianName"]);
    $("#populationModal").text(data[i]["countryPopulation"]);
    $("#infectedModal").text(data[i]["infected"]);
    $("#infectedTodayModal").text(data[i]["infectedToday"]);
    $("#infectedRatioModal").text(data[i]["infectedRatio"] + "%");
    $("#deadModal").text(data[i]["dead"]);
    $("#deadTodayModal").text(data[i]["deadToday"]);
    $("#deadRatioModal").text(data[i]["deadRatio"] + "%");
    $("#curedModal").text(data[i]["cured"]);
    $("#activeModal").text(data[i]["active"]);
    $("#criticalModal").text(data[i]["critical"]);
    $("#countryFlag").attr("src", data[i]["flag"])
    $("#countryDensity").text(data[i]["density"] + " P/Km²")
    $("#countryDetailsModal").modal("show");
    showGraph(data[i]["A2code"]);
  })
})


$(".tableFixHead").on("scroll", function (event) {
  var y = $(this).scrollTop(); 
  if (y > 0) {  
    $(".fakeThead").addClass('shadows'); 
  }
  else { 
    $(".fakeThead").removeClass('shadows'); 
  }
});

$(document).ready(function() {
  $("#logotip").click(function() {
    switchTheme();
  })
})


function switchTheme() {
  if (currentTheme == "light") {
    //$("#logotip").css("color", "black");
    $("#logotip").attr("src", "./static/images/icon-test-dark-alt.png");
    $("html").css("background-color", "#212121")
    $("body").css("background-color", "#212121")

    $("#dataTable").addClass("my-table-dark");
    $(".fakeThead").css("background-color", "#212121");
    
    $("thead th").css("background-color", "#212121")
    $("thead th").css("color", "white")

    $(".modal-content").addClass("elegant-color");
    $(".modal-body").addClass("text-white");
    currentTheme = "dark"
  }
  else {
    // vklopimo light theme
    //$("#logotip").css("color", "white");
    $("#logotip").attr("src", "./static/images/icon-test-alt.png");
    $("html").css("background-color", "white")
    $("body").css("background-color", "white")

    $("#dataTable").removeClass("my-table-dark");
    $(".fakeThead").css("background-color", "white");
    
    $("thead th").css("background-color", "white")
    $("thead th").css("color", "black")

    $(".modal-content").removeClass("elegant-color");
    $(".modal-body").removeClass("text-white");
    currentTheme = "light"
  }
}

var ctxL = document.getElementById("lineChart").getContext('2d');
var myLineChart = new Chart(ctxL, {
  type: 'line',
  data: {
    labels: graphData["dates"].slice(-graphData["SI"]["dead"].length),
    datasets: [
      {
        label: "Umrli",
        data: graphData["SI"]["dead"],
        backgroundColor: [
          'rgba(255, 69, 69, .4)',
        ],
        borderColor: [
          'rgba(255, 69, 69, .8)',
        ],
        borderWidth: 2
      },
      {
        label: "Okuženi",
        data: graphData["SI"]["confirmed"],
        backgroundColor: [
          'rgba(0, 184, 107, .25)',
        ],
        borderColor: [
          'rgba(0, 184, 107, .5)',
        ],
        borderWidth: 2
      },

      /*
      {
        label: "Ozdraveli",
        data: graphData["SI"]["recovered"],
        backgroundColor: [
          'rgba(0, 250, 220, .2)',
        ],
        borderColor: [
          'rgba(0, 213, 132, .7)',
        ],
        borderWidth: 2
      }
      */
    ] 
  },
  options: {
    responsive: true,
    scales: {
      xAxes: [{
        gridLines: {
          color: '#ffeb3b',
          zeroLineColor: "yellow",
          display:false,
        }
      }],
      yAxes: [{
        gridLines: {
          color: '#ffeb3b',
          zeroLineColor: "#ffffff",
          display:false,
        },
        labels: {
          color: 'yellow',
          fontColor: 'red'
        }  
      }]
    },
    legend: {
      position: "bottom"
    },
    elements: {
      point: {
        radius: 0
      }
    }
  }
});

function showGraph(countryCode) {
  myLineChart.data.labels = graphData["dates"].slice(-graphData[countryCode]["confirmed"].length),
  myLineChart.data.datasets[1].data = graphData[countryCode]["confirmed"]
  myLineChart.data.datasets[0].data = graphData[countryCode]["dead"]
  //myLineChart.data.datasets[2].data = graphData[countryCode]["recovered"]
  myLineChart.update();
}

function modeSwitch() {
  $("#globeSwitch")[0].classList.toggle("fa-globe-europe");
  if (region == "Europe") {
    region = ""
    $("#globeText").text(" Svet\xa0\xa0");
    $("#globalDeaths").text(globalData["deaths"]);
    $("#globalRecovered").text(globalData["recovered"]);
    $("#globalCases").text(globalData["cases"]);
  }
  else {
    region = "Europe";
    $("#globeText").text(" Evropa");
    $("#globalDeaths").text(europeData["deaths"]);
    $("#globalRecovered").text(europeData["recovered"]);
    $("#globalCases").text(europeData["cases"]);
  };
  tableBodyCreate(region)
  colorCountry();
}

if ('serviceWorker' in navigator) {
  // sw.js can literally be empty, but must exist
  navigator.serviceWorker.register('/sw.js');
}