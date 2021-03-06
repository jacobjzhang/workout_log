const { Col, Button, Form, FormGroup, Label, Input, FormText, Table } = Reactstrap;

class WorkoutSet extends React.Component {
  render() {
    const set = this.props.set;

    return(
      <tr>
        <th scope="row">{set.exercise_id}</th>
        <td>{set.order}</td>
        <td>{set.weight}</td>
        <td>{set.reps}</td>
      </tr>
    )
  }
}

class WorkoutTable extends React.Component {
  render() {
    const workout = this.props.workout;

    return (
      <div>
        <h1>Workout # {workout.id}</h1>
        <Table>
          <thead>
            <tr>
              <th>Exercise</th>
              <th>Set #</th>
              <th>Weight</th>
              <th>Reps</th>
            </tr>
          </thead>
          <tbody>
            {workout.exercises.map((exercise) => {
              return exercise.sets.map((set) => {
                return <WorkoutSet set={set} />;
              })
            })}
          </tbody>
        </Table>
      </div>
    )
  }
}

class Workouts extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      workouts: []
    };
  }

  componentWillMount() {
    fetch(`http://localhost:5001/workouts`)
      .then((response) => response.json())
      .then((responseJSON) => {
        const workouts = responseJSON;
        this.setState({ workouts });
      });
  }
  
  render() {
    const workouts = this.state.workouts;

    return (
      <div>
        {
          workouts.map((workout) => {
            return <WorkoutTable workout={workout} />;
          })
        }
      </div>
    )
  }
}

class AddSet extends React.Component {
  render() {
    const setNum = this.props.setNum;

    const exNum = `exercise${setNum}`;
    const weightNum = `weight${setNum}`;
    const repsNum = `reps${setNum}`;

    return(
      <div>
        <h4>Set #{setNum}</h4>
        <FormGroup>
          <Label for={exNum}>Select</Label>
          <Input type="select" name={exNum} id={exNum}>
            {this.props.exerciseOptions}
          </Input>
        </FormGroup>

        <FormGroup>
          <Label for={weightNum}>Weight</Label>
          <Input type="text" name={weightNum} id={weightNum} placeholder="__ lbs" />
        </FormGroup>

        <FormGroup>
          <Label for={repsNum}>Reps</Label>
          <Input type="text" name="reps" id={repsNum} placeholder="__ reps" />
        </FormGroup>
      </div>
    )
  }
}

class AddWorkout extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      exercises: [],
      numSets: 1
    };
  }

  componentWillMount() {
    fetch(`http://localhost:5001/exercises`)
      .then((response) => response.json())
      .then((responseJSON) => {
        const exercises = responseJSON;
        this.setState({ exercises });
      });
  }

  addSet(event) {
    console.log(this.state)
    const currentSets = this.state.numSets;
    this.setState({numSets: currentSets + 1});
  }

  handleSubmit(event) {
    event.preventDefault();

    const data = new FormData(event.target);
    
    fetch('http://localhost:5001/add_workout', {
      method: 'POST',
      body: data,
    });
  }  
  
  render() {
    const exerciseOptions = this.state.exercises.map((ex) => {
      return <option value={ex.id}>{ex.name}</option>
    });

    let setsToAdd = [];
    console.log(this.state.numSets)
    for (let i = 0; i < this.state.numSets; i++) {
      setsToAdd.push(<AddSet setNum={i} exerciseOptions={exerciseOptions} />)
    }

    return (
      <Form method="POST" action="http://localhost:5001/add_workout" onSubmit={this.handleSubmit}>

        {setsToAdd}

        <input type="hidden" name="exercise_count" value="1" />

        <Button>Submit</Button>

        <Button onClick={() => this.addSet()}>Add Set</Button>
      </Form>
    );
  }
};

ReactDOM.render(
  <Col xs="6">
    <Workouts />
    <AddWorkout />
  </Col>,
  document.getElementById('app')
);