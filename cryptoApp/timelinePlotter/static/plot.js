function getChangepointPlot(changePoints, maxTime, minTime, xScale, colors) {
  bands = [];
  for (index in changePoints) {
    if (index == changePoints.length - 1) {
      bands.push({
        low: changePoints[index].time * 1000,
        high: maxTime + 10000000,
        color: colors[index % 2]
      });
      break;
    }

    if (index == 0) {
      bands.push({
        low: minTime - 10000000,
        high: changePoints[index].time * 1000,
        color: colors[(index + 1) % 2]
      });
    }

    bands.push({
      low: changePoints[index].time * 1000,
      high: changePoints[parseInt(index) + 1].time * 1000,
      color: colors[index % 2]
    });
  }

  var bandPlot = new Plottable.Plots.Rectangle()
    .y(0)
    .y2(function() {
      return bandPlot.height();
    })
    .x(function(d) {
      return d.low;
    }, xScale)
    .x2(function(d) {
      return d.high;
    })
    .attr("fill", function(d) {
      return d.color;
    })
    .addDataset(new Plottable.Dataset(bands));

  return bandPlot;
}

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

      minTime = Infinity;
      maxTime = -1;

      for (dataPoint in data) {
        pointTime = data[dataPoint]["endTime"] * 1000;

        minTime = Math.min(minTime, pointTime);
        maxTime = Math.max(maxTime, pointTime);

        numSubmissions.push({
          y: data[dataPoint]["submissions"],
          x: pointTime
        });
        submissionScore.push({
          y: data[dataPoint]["submissionScores"],
          x: pointTime
        });
        numComments.push({
          y: data[dataPoint]["comments"],
          x: pointTime
        });
        commentScore.push({
          y: data[dataPoint]["commentScores"],
          x: pointTime
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

      plots = [plot, cryptoPlot];

      if (input.changePoints.length > 0) {
        plot = [
          getChangepointPlot(input.changePoints, maxTime, minTime, xScale, [
            "#ffffff",
            "#f0f0f0"
          ])
        ];
        plots = plot.concat(plots);
      }

      var group = new Plottable.Components.Group(plots);
      var chart = new Plottable.Components.Table([
        [null, null, legend, null, null],
        [mediaLabel, yAxis, group, yAxis2, cryptoLabel],
        [null, null, xAxis, null, null]
      ]);

      chart.renderTo("svg#plot");
    });
  });
}

var input = {
  filepath: "timeline.json",
  outputSvg: "plot",
  crypto: "crypto.json",
  changePointFile: "changepoints.json"
};

d3.json(input.changePointFile, function(error3, changePoints) {
  changePointList = [];

  if (changePoints != null) {
    changePointList = changePoints;
  }

  input.changePoints = changePointList;

  plotAttribute(input);
});
