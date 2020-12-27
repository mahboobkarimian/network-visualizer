function getWidth() {
    return Math.max(
      document.body.scrollWidth,
      document.documentElement.scrollWidth,
      document.body.offsetWidth,
      document.documentElement.offsetWidth,
      document.documentElement.clientWidth
    );
}
var menu = d3.select('.menu').node();
var h_menu = menu.getBoundingClientRect().height;
function getHeight() {
    return document.documentElement.clientHeight-Math.round(h_menu);
}
var width = getWidth(), height = getHeight();
var svg = d3.select("body")
    .append("svg")
    .attr("width", width)
    .attr("height", height);
var container = svg.append('g');

var zoom = d3.zoom().on('zoom', zoomed);
var simulation;
var color = d3.scaleOrdinal(["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854", "#ffd92f", "#e5c494", "#b3b3b3"]);

window.addEventListener("resize", updatewin);
d3.select("#Node_labels").on("change",update_label);
update_label();
d3.select("#Scroll_zoom").on("change",control_zoom);
control_zoom();
d3.select("#refresh").on("change",refresh_interval);
refresh_interval();
d3.select("#refresh_now").on("click", function(d){
                                redraw();
                                });
d3.select("#reset").on("click", function(d){
                                    svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity);
                                    redraw();
                                });

function draw_graph() {
    d3.json("force/force.json", function (error, graph) {
        if (error) throw error;
        
        simulation = d3.forceSimulation()
            .force("link", d3.forceLink()
                .id(function (d) { return d.id;})
                .distance(90))
            .force("charge", d3.forceManyBody()
                .strength(function (d) { return -50*d.degree;})
                .distanceMin([100])
                .distanceMax([500]))
            .force("center", d3.forceCenter(getWidth()/2, getHeight()/2));

        var degreeSize = d3.scaleLinear()
            .domain([d3.min(graph.nodes, function(d) {
                return d.degree; }),d3.max(graph.nodes, function(d) {return d.degree; })])
            .range([6,26]);

        var link = container.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(graph.links)
            .enter().append("line")
            .attr('marker-end','url(#arrowhead)');

        
        var node = container.append("g")
            .attr("class", "nodes")
            .selectAll("g")
            .data(graph.nodes)
            .enter().append("g")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
            
        var circles = node.append("circle")
            .attr("r", function(d) { return degreeSize(d.degree); })
            .attr("fill", function(d) {
                if(d.id == 'BR') return "crimson";
                return color(d.id);});
            
        
        var lables = node.append("text")
            .text(function(d) {
                id_splt = d.id.split(":")
                id_size = id_splt.length
                lbl1 = id_splt[id_size-2]
                lbl2 = id_splt[id_size-1]
                lbl = [lbl1 , lbl2]
                return lbl.join(":");
            })
            .attr('x', function(d) { return degreeSize(d.degree); })
            .attr('y', (function(d) { return degreeSize(d.degree)/2; }));

        node.append("title")
            .text(function (d) {
                return d.id;
            });

        simulation
            .nodes(graph.nodes)
            .on("tick", ticked);

        simulation.force("link")
            .links(graph.links);

        function ticked() {
            link
                .attr("x1", function (d) {
                    return d.source.x;
                })
                .attr("y1", function (d) {
                    return d.source.y;
                })
                .attr("x2", function (d) {
                    return d.target.x;
                })
                .attr("y2", function (d) {
                    return d.target.y;
                });

            node
                .attr("transform", function(d) {
                    return "translate(" + d.x + "," + d.y + ")";
                })
        }
    });
}
draw_graph();

function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0.1);
    d.fx = null;
    d.fy = null;
}

function zoomed() {
    container.attr("transform", "translate(" + d3.event.transform.x + ", " + d3.event.transform.y + ") scale(" + d3.event.transform.k + ")");
}

function updatewin() {
    svg
    .attr("width", getWidth())
    .attr("height", getHeight());
}

function redraw(d) {
    container.selectAll("g").remove();
    draw_graph();
}

function update_label(d){
    if(d3.select("#Node_labels").property("checked")){
        d3.selectAll("text").style("display", "inherit");
    } else {
        d3.selectAll("text").style("display", "none");
    }
}

function control_zoom(d){
    if(d3.select("#Scroll_zoom").property("checked")){
        svg.call(d3.zoom().on('zoom', zoomed));
    } else {
        svg.on('.zoom', null);
    }
}

var t;
function refresh_interval(d){
    if(d3.select("#refresh").property('checked')){
        var t_value = d3.select("#interval").property("value");
        console.log(t_value);
        t = d3.interval(redraw,t_value*1000);
    } else {
        if(t != null) t.stop();
    }
}