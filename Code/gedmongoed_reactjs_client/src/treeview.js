import React from 'react';
import Tree from 'react-d3-tree';
import { Container, Row, Col, Form, Button } from 'react-bootstrap';
import CoupleNode from './CoupleNode';

const orientation = 'vertical';

const translate = {
  x: 0,
  y: 50
};


// This is a simplified example of an org chart with a depth of 2.
// Note how deeper levels are defined recursively via the `children` property.

const OrgChart = [
  {
    name: 'Parent',
    children: [
      {
        name: 'Child 1',
        depth: 2, // définit la profondeur du noeud enfant au même niveau que son parent
      },
      {
        name: 'Child 2',
      },
    ],
  },
  {
    name: 'Parent2',
    children: [
      {
        name: 'Child 3',
        depth: 2, // définit la profondeur du noeud enfant au même niveau que son parent
      },
      {
        name: 'Child 4',
      },
    ],
  }
];

export default function OrgChartTree() {

  return (
    <Container fluid>
      <Row className="justify-content-center mt-5" >
        <Col md={6}>
          <div id="treeWrapper" style={{ height: 100 }}>
            <Tree data={OrgChart} orientation={orientation} translate={translate} />
          </div>
        </Col>
      </Row>
    </Container>
  );
}
