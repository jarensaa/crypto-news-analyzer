function plotAttribute(input) {
  d3.json(input.filepath, function(error, data) {
    d3.json(input.crypto, function(error2, cryptoData) {
      var cs = new Plottable.Scales.Color();
      var colors = ["#4c4cff", "#9999ff", "#ff4c4c", "#ff9999"];

      cs.range(colors);
      cs.domain([
        "Number of submissions",
        "Score on submissions",
        "Number of comments",
        "Score on comments"
      ]);

      numSubmissions = [];
      submissionScore = [];
      numComments = [];
      commentScore = [];

      for (dataPoint in data) {
        numSubmissions.push({
          y: data[dataPoint]["submissions"],
          x: data[dataPoint]["endTime"] * 1000
        });
        submissionScore.push({
          y: data[dataPoint]["submissionScores"],
          x: data[dataPoint]["endTime"] * 1000
        });
        numComments.push({
          y: data[dataPoint]["comments"],
          x: data[dataPoint]["endTime"] * 1000
        });
        commentScore.push({
          y: data[dataPoint]["commentScores"],
          x: data[dataPoint]["endTime"] * 1000
        });
      }

      var legend = new Plottable.Components.Legend(cs);

      var xScale = new Plottable.Scales.Time();
      var yScale = new Plottable.Scales.Linear();
      var yScale2 = new Plottable.Scales.Linear();

      var xAxis = new Plottable.Axes.Time(xScale, "bottom");
      var yAxis = new Plottable.Axes.Numeric(yScale, "left");
      var yAxis2 = new Plottable.Axes.Numeric(yScale2, "right");

      var cryptoPlot = new Plottable.Plots.Line()
        .addDataset(new Plottable.Dataset(cryptoData))
        .x(function(data) {
          return data.time * 1000;
        }, xScale)
        .y(function(data) {
          return data.open;
        }, yScale2);

      var plot = new Plottable.Plots.StackedArea()
        .addDataset(new Plottable.Dataset(numSubmissions, { color: colors[0] }))
        .addDataset(
          new Plottable.Dataset(submissionScore, { color: colors[1] })
        )
        .addDataset(new Plottable.Dataset(numComments, { color: colors[2] }))
        .addDataset(new Plottable.Dataset(commentScore, { color: colors[3] }))
        .x(function(d) {
          return d.x;
        }, xScale)
        .y(function(d) {
          return d.y;
        }, yScale)
        .attr("fill", function(d, i, ds) {
          return ds.metadata().color;
        });

      var mediaLabel = new Plottable.Components.AxisLabel(
        "Social media activity",
        "270"
      );
      var cryptoLabel = new Plottable.Components.AxisLabel(
        "Bitcoin price ($)",
        "90"
      );

      var group = new Plottable.Components.Group([plot, cryptoPlot]);
      var chart = new Plottable.Components.Table([
        [null, null, legend, null, null],
        [mediaLabel, yAxis, group, yAxis2, cryptoLabel],
        [null, null, xAxis, null, null]
      ]);

      chart.renderTo("svg#plot");
    });
  });
}

input = {
  filepath: "timeline.json",
  outputSvg: "plot",
  crypto: "crypto.json"
};

plotAttribute(input);
