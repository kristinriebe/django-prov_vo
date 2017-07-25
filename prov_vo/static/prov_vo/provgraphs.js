/* script based on d3-examples, see e.g. https://bost.ocks.org/mike/sankey/
 * and http://bl.ocks.org/mbostock/4062045;
 * adjusted by Kristin Riebe, AIP
 */

var margin = {top: 1, right: 1, bottom: 6, left: 1},
    width = 960 - margin.left - margin.right,
    height = 600 - margin.top - margin.bottom;

var formatNumber = d3.format(",.0f"),
    format = function(d) { return formatNumber(d) + ""; },
    color = d3.scale.category20();

var svg = d3.select("#chart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var sankey = d3.sankey()
    .nodeWidth(15)
    .nodePadding(10)
    .size([width, height]);

var path = sankey.link();

// load the data
//var jsonurl = 'graphjson' // append graphjson to the path to get json representation of data

var url_graphjson = d3.select("#url_graphjson").text();
var jsonurl = url_graphjson;

d3.json(jsonurl, function(prov) {
  sankey
      .nodes(prov.nodes)
      .links(prov.links)
      .layout(32);

  // add links
  var link = svg.append("g").selectAll(".link")
      .data(prov.links)
    .enter().append("path")
      .attr("class",  function(d) { return "link sankey " + d.type;} )
      .attr("d", path)
      .style("stroke-width", function(d) { return Math.max(0.5, 0.5*d.dy); })
      .sort(function(a, b) { return b.dy - a.dy; });

  link.append("title")
      .text(function(d) { return d.source.name + " → " + d.target.name + "\n" + "["+d.type+"]"; });

  // add nodes
  var node = svg.append("g").selectAll(".node")
      .data(prov.nodes)
    .enter().append("g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })
    .call(d3.behavior.drag()
      .origin(function(d) { return d; })
      .on("dragstart", function() { this.parentNode.appendChild(this); })
      .on("drag", dragmove));

  // add rectangles for nodes
  node.append("rect")
      .attr("height", function(d) { return d.dy; })
      .attr("width", sankey.nodeWidth())
      .attr("class", function(d) { return d.type; })
    .append("title")
      .text(function(d) { return d.name + "\n" + "["+d.type+"]"; });

  // node annotation
  node.append("text")
      .attr("x", -6)
      .attr("y", function(d) { return d.dy / 2; })
      .attr("dy", ".35em")
      .attr("text-anchor", "end")
      .attr("transform", null)
      .text(function(d) { return d.name; })
    .filter(function(d) { return d.x < width / 2; })
      .attr("x", 6 + sankey.nodeWidth())
      .attr("text-anchor", "start");

  function dragmove(d) {
    d3.select(this).attr("transform",
      "translate(" + (
        d.x = Math.max(0, Math.min(width - d.dx, d3.event.x))
        ) + "," + (
        d.y = Math.max(0, Math.min(height - d.dy, d3.event.y))
        ) + ")");
    sankey.relayout();
    link.attr("d", path);
  }
});


/* Force-directed graph layout */

// First draw some lines for a simple legend
var svg3 = d3.select("#force-legend").append("svg")
            .attr("width", 300)
            .attr("height", 80);

var lineData = [
  { "x1": 5, "y1": 15, "x2": 40, "y2": 15, "name": "used" },
  { "x1": 5, "y1": 30, "x2": 40, "y2": 30, "name": "wasGeneratedBy" },
  { "x1": 5, "y1": 45, "x2": 40, "y2": 45, "name": "hadMember" },
  { "x1": 5, "y1": 60, "x2": 40, "y2": 60, "name": "hadStep" },
  { "x1": 155, "y1": 15, "x2": 190, "y2": 15, "name": "wasAssociatedWith" },
  { "x1": 155, "y1": 30, "x2": 190, "y2": 30, "name": "wasAttributedTo" },
  { "x1": 155, "y1": 45, "x2": 190, "y2": 45, "name": "wasDerivedFrom" },
  { "x1": 155, "y1": 60, "x2": 190, "y2": 60, "name": "wasInformedBy" },
  ];

var lines = svg3.selectAll("line")
            .data(lineData)
            .enter()
            .append("line");

var lineAttributes = lines
      .attr("x1", function (d) { return d.x1; })
      .attr("y1", function (d) { return d.y1; })
      .attr("x2", function (d) { return d.x2; })
      .attr("y2", function (d) { return d.y2; })
      .attr("stroke-width", 2)
      .attr("stroke", "black")
            .attr("class", function (d) { return "link "+ d.name });

var text = svg3.selectAll("text")
            .data(lineData)
            .enter()
            .append("text");

var textLabels = text
            .attr("x", function(d) { return d.x2+10; })
            .attr("y", function(d) { return d.y2+4; })
            .text( function (d) { return d.name; })
            .attr("font-family", "sans-serif")
            .attr("font-size", "20px")
            .attr("class", function (d) { return "marker "+ d.name })
            .attr("stroke-width", 0);

var width2 = 960,
    height2 = 500;

var svg2 = d3.select("#force-graph").append("svg")
      .attr("width", width2)
      .attr("height", height2);

var defs = svg2.append("svg:defs");

var jsonurl = url_graphjson;
d3.json(jsonurl, function(prov) {

  var force = d3.layout.force()
      .nodes(prov.nodes)
      .links(prov.links)
      .size([width2, height2])
      .linkDistance(60)
      .charge(-300)
      .on("tick", tick)
      .start();

  // Per-type markers, as they don't inherit styles.
  svg2.append("defs").selectAll("marker")
      .data(["used", "wasGeneratedBy", "wasAssociatedWith", "wasAssociatedWith", "hadMember", "wasDerivedFrom", "hadStep", "wasInformedBy"])
    .enter().append("marker")
      .attr("id", function(d) { return d; })
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 15)
      .attr("refY", -1.5)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
    .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("class", function(d) { return "marker "+d; });

  var path = svg2.append("g").selectAll("path")
      .data(force.links())
    .enter().append("path")
      .attr("class", function(d) { return "link " + d.type; })
      //.attr("marker-end", marker('#0000ff'));
      .attr("marker-end", function(d) { return "url(#" + d.type + ")"; });

  var shapes = svg2.append("g").selectAll(".shapes")
      .data(force.nodes())
    .enter();

  var ellipse = shapes.append("ellipse")
      .filter(function(d){ return d.type == "entity"; })
      .attr("class", function(d) { return d.type; })
      .attr("rx", 15)
      .attr("ry", 10)
      .attr("cx", 0)
      .attr("cy", 0)
      .call(force.drag);

/*  var circle = shapes.append("circle")
      .filter(function(d){ return d.type == "agent"; })
      .attr("class", function(d) { return d.type; })
      .attr("r", 8)
      .call(force.drag);
*/
  var polygon = shapes.append("path")
      .filter(function(d){ return d.type == "agent"; })
      .attr("class", function(d) { return d.type; })
      .attr("d", "M-15,7 L-15,-5 L0,-12 L15,-5 L15,7 L-15,7")
      .call(force.drag);

  var rectangle = shapes.append("rect")
      .filter(function(d){ return d.type == "activity"; })
      .attr("class", function(d) { return d.type; })
      .attr("x", -14)
      .attr("y", -9)
      .attr("width", 28)
      .attr("height", 18)
      .call(force.drag);

  var rectangle2 = shapes.append("rect")
      .filter(function(d){ return d.type == "activityFlow"; })
      .attr("class", function(d) { return d.type; })
      .attr("x", -14)
      .attr("y", -9)
      .attr("width", 28)
      .attr("height", 18)
      .call(force.drag);

  var text = svg2.append("g").selectAll("text")
      .data(force.nodes())
    .enter().append("text")
      .attr("x", 16)
      .attr("y", ".75em")
      .text(function(d) { return d.name; });

  // Use elliptical arc path segments to doubly-encode directionality.
  function tick() {
    path.attr("d", linkArc);
    ellipse.attr("transform", transform);
    polygon.attr("transform", transform);
    rectangle.attr("transform", transform);
    rectangle2.attr("transform", transform);
    text.attr("transform", transform);
  }

  function linkArc(d) {
    var dx = d.target.x - d.source.x,
        dy = d.target.y - d.source.y,
        dr = Math.sqrt(dx * dx + dy * dy);
    return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y;
  }

  function transform(d) {
    return "translate(" + d.x + "," + d.y + ")";
  }

});
